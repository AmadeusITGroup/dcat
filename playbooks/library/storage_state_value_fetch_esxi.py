'''
 State File updation custom module
'''
import time
from io import StringIO
import warnings
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
from azure.data.tables import TableClient, UpdateMode
import requests
pd.options.mode.chained_assignment = None
warnings.simplefilter(action='ignore', category=FutureWarning)


DOCUMENTATION = r'''
---
module: Update module results to reference point to acheive idempotency logic

description: Update module results to reference point to acheive idempotency logic.

version_added: "1.0.0"

options:
    hostname:
        description: Hostname of the DECO server.
        required: true
        type: str

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_ref:
            hostname: "{{hostname}}"
          register: update_status
          delegate_to: localhost
'''

def write_data(connection_string,table_name,hostname):
    
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)

    try:   
        host_detail = service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        host_detail = None

    if host_detail:
        #print("already Exists and grepping existing value")
        idempotent_obj = {}
        info_storage_cleanup = host_detail['info_storage_cleanup']
        host_info = host_detail['host_info']
        idempotent_obj = {}
        idempotent_obj['info_storage_cleanup'] = info_storage_cleanup
        idempotent_obj['host_info'] = host_info
    else:
        new_entry = {'RowKey':hostname,'PartitionKey':hostname[:2],'info_storage_cleanup':'F','host_info':'F'}
        temp = service.create_entity(new_entry)
        idempotent_obj = {}
        hostname=hostname
        info_storage_cleanup='F'
        host_info='F'
        idempotent_obj['info_storage_cleanup'] = info_storage_cleanup
        idempotent_obj['host_info'] = host_info
    return idempotent_obj

def main():
    returnvalue = {}
    table_name = "EsxiServerStorageDetails"
    fields = {
        "connection_string":{"required":True,"type":"str"},
        "hostname":{"required":True,"type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(connection_string= module.params["connection_string"],
                            table_name= table_name,
                            hostname= module.params["hostname"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["module_update"] = "[ERROR]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
