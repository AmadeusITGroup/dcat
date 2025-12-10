import pyarrow
import os
import requests
import configparser
import pandas as pd
from azure.data.tables import TableClient, UpdateMode, TableServiceClient
from typing import Union
from ansible.module_utils.basic import AnsibleModule
from pyarrow import parquet


def convert_to_pyarrow_table(connection_string, table_name):
  try:
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)
    entities = service.list_entities(results_per_page=1000)
    entity_list = []
    for e in entities:
      entity_list.append(e)
    del entities
    df = pd.DataFrame(entity_list)

    pa_table = pyarrow.Table.from_pandas(df)
    return pa_table, None

  except Exception as excp:
    return None, excp


def writing_data_to_remote_location(sas_token, file_name):
  ## Basic configuration
  local_file_path = os.path.abspath(file_name)  # Path to your local  file

  # blob storage URL with sas_token
  blob_storage_url = f"{azure_blob_account_url}/{azure_blob_container_name}/{file_name}?{sas_token}"

  # Set the required headers for the upload
  headers = {
      "x-ms-blob-type": "BlockBlob",
      "x-ms-version": "2020-06-12"
  }

  upload_response = {
     "file_name": file_name,
     "upload_status": False,
     "message": "",
     "url": blob_storage_url,
     "file path": local_file_path
  }

  try:
    # Read the  file content
    with open(local_file_path, "rb") as file_data:
      # Make a PUT request to upload the file
      response = requests.put(url=blob_storage_url, headers=headers, data=file_data)
    # Check the response
    if response.status_code == 201:
      upload_response["upload_status"] = True
      upload_response["message"] = f"File {local_file_path} successfully uploaded to {azure_blob_name} in container {azure_blob_container_name}."
    else:
      upload_response["message"] = f"Failed to upload file. Status code:{response.status_code} \n Response: {response.text}"
  except Exception as e:
     upload_response["message"] = f"An error occurred: {e}"

  return upload_response


def read_data_from_tables(connection_string, sas_token, table_name: Union[str, list[str]]):

  vals = {
      "parquet_data": {} if isinstance(table_name, list) else None,
      "parquet_location": {} if isinstance(table_name, list) else None,
      "file_upload_response": {} if isinstance(table_name, list) else None,
      "execption": None,
  }

  try:
    if isinstance(table_name, str):
      pa_table, excp = convert_to_pyarrow_table(connection_string=connection_string, table_name=table_name)
      parquet_file_local = f"{table_name}.parquet" if ENV_NAME == "prod" else f"DEV_{table_name}.parquet" 

      if excp is None:
          vals["parquet_data"] = pa_table.to_pandas().to_dict(orient="records")
          vals["parquet_location"] = parquet_file_local
          parquet.write_table(pa_table, parquet_file_local)

          vals["file_upload_response"] = writing_data_to_remote_location(sas_token=sas_token, file_name=vals["parquet_location"])
      else:
          vals["execption"] = excp

    elif isinstance(table_name, list):
      for table in table_name:
        try:
          pa_table, excp = convert_to_pyarrow_table(connection_string, table)
          parquet_file_local = f"{table}.parquet" if ENV_NAME == "prod" else f"DEV_{table}.parquet"

          if excp is None:
            vals["parquet_data"][table] = pa_table.to_pandas().to_dict(orient="records")
            vals["parquet_location"][table] = parquet_file_local
            
            parquet.write_table(pa_table, parquet_file_local)

            vals["file_upload_response"][table] = writing_data_to_remote_location(sas_token=sas_token, file_name=vals["parquet_location"][table])
          else:
            if vals["execption"] is None:
              vals["execption"] = {}
            vals["execption"][table] = excp
        except Exception as ex:
          if vals["execption"] is None:
            vals["execption"] = {}
          vals["execption"][table] = ex

  except Exception as ex:
      vals["execption"] = ex

  return vals


def run_module():
    fields = { 
              "connection_string":{"required":True,"type":"str"},
              "sas_token": {"required":True,"type":"str"},
              "account_url": {"required":True,"type":"str"},
              "container_name": {"required":True,"type":"str"},
              "blob_name": {"required":True,"type":"str"},
              "env_name": {"required":False,"type":"str", "default": "prod"}
              }

    module = AnsibleModule(argument_spec = fields)

    global azure_blob_account_url, azure_blob_container_name, azure_blob_name, ENV_NAME
    
    azure_blob_account_url = module.params["account_url"]
    azure_blob_container_name = module.params["container_name"]
    azure_blob_name = module.params["blob_name"]
    ENV_NAME = module.params["env_name"].lower()

    table_name = ["TRdetails", "CRdetails", "metadataDetails", "hostDetails", "PhysicalServerDetails", "PhysicalServerStorageDetails", "EsxiServerDetails", "EsxiServerStorageDetails", "CMDBAccounts"]
    dev_table_name = ["TRdetails", "CRdetails", "metadataDetails", "hostDetails", "PhysicalServerDetails", "PhysicalServerStorageDetails", "EsxiServerDetails", "EsxiServerStorageDetails", "CMDBAccounts"]
    
    if ENV_NAME == "dev":
      table_name = dev_table_name

    returnvalue = {}
    try: 
        upd = read_data_from_tables(connection_string= module.params["connection_string"],
                                    table_name= table_name, sas_token=module.params["sas_token"]
                                    )
        returnvalue = upd
        module.exit_json(**returnvalue)

    except Exception as ex:
        returnvalue["module_update"]="Exception occurred ==>> " +str(ex)
        module.exit_json(**returnvalue)


if __name__ == '__main__':
    run_module()