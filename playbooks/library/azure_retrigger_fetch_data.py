from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_entity(connection_string,hostname):

    graceperiod_flag = 'False'
    
    vm_service = TableClient.from_connection_string(conn_str=connection_string,table_name="hostDetails")
    phy_service = TableClient.from_connection_string(conn_str=connection_string,table_name="PhysicalServerDetails")

    try:   
        vm_detail = vm_service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        vm_detail = None

    try:   
        phy_detail = phy_service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        phy_detail = None


    if vm_detail:
        
        vm_poweroff_before_gp = vm_detail['vm_poweroff_before_gp']

        if vm_poweroff_before_gp == 'T':
            graceperiod_flag = 'True'

    else:

        shutdown_bgp = phy_detail['shutdown_bgp']

        if shutdown_bgp == 'T':
            graceperiod_flag = 'True'

    
    return graceperiod_flag


def run_module():

    fields = {
        "connection_string":{"required":True,"type":"str"},
        "hostname":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_entity(connection_string= module.params["connection_string"], hostname= module.params["hostname"])
        if module_update:
            returnvalue["module_update"] = module_update
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["module_update"] = module_update
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["module_update"]="Exception occurred while fetching entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()