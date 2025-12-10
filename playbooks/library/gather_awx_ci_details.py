from azure.data.tables import TableClient, UpdateMode
import configparser,requests
from requests.auth import HTTPBasicAuth
from ansible.module_utils.basic import AnsibleModule


def create_entity(cr,connection_string):
    
    metadata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="metadataDetails")
    cr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="CRdetails")
    hostdata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="hostDetails")

    cr_fil = "PartitionKey eq '{}'".format(cr)

    idempotent_obj = {}
    awx_job_list=[]
    ci_list={}

    try:  
        metadata_details = list(metadata_service.query_entities(query_filter= cr_fil,select=["RowKey"]))
    except Exception as e:
        metadata_details = e

    try:
        cr_details = list(cr_service.query_entities(query_filter= cr_fil,select=["RowKey"]))
    except Exception as e:
        cr_details = e


    for data in metadata_details:
        awx_job_list.append(data["RowKey"]) 

    for ci in cr_details:
        ci_name = ci["RowKey"]
        host_filter="RowKey eq '{}'".format(ci_name)
        try:
            host_details = list(hostdata_service.query_entities(query_filter=host_filter,select=["instanceid"]))
        except Exception as e:
            host_details=e
        
        for host in host_details:
            instance_id = host["instanceid"]
            ci_list[ci_name] = instance_id

    
    idempotent_obj["awx_jobs"] = awx_job_list
    idempotent_obj["ci_list"] = ci_list
    

    return idempotent_obj


def run_module():

    fields = {
        "cr":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(cr= module.params["cr"],connection_string= module.params["connection_string"])
        if create_entity_result:
            returnvalue["create_entity_result"] = create_entity_result
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["create_entity_result"] = create_entity_result
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["create_entity_result"]="Exception occurred while creating entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()