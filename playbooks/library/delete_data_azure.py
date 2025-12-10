from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_entity(hostname):

    connection_string="DefaultEndpointsProtocol=https;AccountName=awxdcatdev;AccountKey=p0GybDYuCXIFrNDCnO7drvoA0PieEwdrkEOJMoonf0UFMBWw//km5DqES942kyJ7NjZ4V+VShZXJ+ASttmsS3w==;EndpointSuffix=core.windows.net"
    
    service = TableClient.from_connection_string(conn_str=connection_string,table_name="hostDetails")

    delete_detail = ""
    try:   
        host_detail = service.get_entity(partition_key="vm", row_key=hostname)
        if host_detail:
            delete_detail = service.delete_entity(partition_key="vm", row_key=hostname)
        else:
            delete_detail = "No details found"
    except Exception as e:
        host_detail = None

    
    return delete_detail


def run_module():

    fields = {
        "hostname":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_entity(hostname= module.params["hostname"])
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