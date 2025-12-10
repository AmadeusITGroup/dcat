from io import StringIO
import warnings
import pandas as pd
from azure.data.tables import TableClient, UpdateMode
from ansible.module_utils.basic import AnsibleModule
import requests
import configparser
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
    module_name:
        description: module name of the DECO process.
        required: true
        type: str
    status:
        description: status of the module eg> (True or False)
        required: true
        type: str

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_module_vals:
            hostname: "{{hostname}}"
            module_name: "{{module_name}}"
            status: "{{ status }}"
          register: update_status
          delegate_to: localhost
'''


def write_data(connection_string,table_name,hostname,module_name,status):
    
    new_data = []
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)

    try:
        host_detail = service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        host_detail = "No details found " + str(e)

    if host_detail:
        new_entry = {'PartitionKey':hostname[:2],'RowKey':hostname,module_name:status}
        temp = service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        new_data.append(module_name+" : successfully updated for host " + hostname)
        
    else:
        new_data.append(module_name+" not found and unable to update for host "+ hostname)
            
    return new_data


def main():
    returnvalue = {}
    table_name = "PhysicalServerDetails"
    fields = {
        "connection_string":{"required":True,"type":"str"},
        "hostname":{"required":True,"type":"str"},
        "module_name":{"required":True,"type":"str"},
        "status":{"required":True,"type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(connection_string= module.params["connection_string"],
                            table_name= table_name,
                            hostname= module.params["hostname"],
                            module_name= module.params["module_name"],
                            status= module.params["status"])
        returnvalue["state_update"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["state_update"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()