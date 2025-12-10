from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_entity(connection_string,table_name,hostname,module_name,status):
    
    new_data = []
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)

    try:
        host_detail = service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        host_detail = "No details found " + str(e)
    
    if host_detail:
        new_entry = {'PartitionKey':hostname[:2],'RowKey':hostname,module_name:status}
        temp = service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        new_data.append("status updated for host " + hostname)
        
    else:
        new_data.append("Unable to update for host " + hostname)
            
    return new_data



def run_module():

    table_name = "hostDetails"
    
    fields = {
        "connection_string":{"required":True,"type":"str"},
        "hostname":{"required":True,"type":"str"},
        "module_name":{"required":True,"type":"str"},
        "status":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_entity(connection_string= module.params["connection_string"],
                                  table_name= table_name,
                                  hostname= module.params["hostname"],
                                  module_name= module.params["module_name"],
                                  status= module.params["status"])
        if module_update:
            returnvalue["module_update"] = module_update
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["module_update"] = module_update
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["module_update"]="Exception occurred while creating entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()