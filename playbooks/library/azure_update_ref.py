from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_entity(connection_string,table_name,hostname):
    
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)

    try:   
        host_detail = service.get_entity(partition_key=hostname[:2], row_key=hostname)
    except Exception as e:
        host_detail = None

    if host_detail:
        hostname = host_detail['RowKey']
        partition_key = host_detail['PartitionKey']
        os = host_detail['os']
        os_fetch_status = host_detail['os_fetch_status']
        application_validation = host_detail['app_validation']
        network = host_detail['network']
        sanstorage = host_detail['sanstorage']
        nasstorage = host_detail['nasstorage']
        backup = host_detail['backup']
        dns = host_detail['dns']
        vm_poweroff = host_detail['vm_poweroff']
        vm_delete = host_detail['vm_delete']
        cmdb = host_detail['cmdb']
        vm_poweroff_before_gp = host_detail['vm_poweroff_before_gp']
        vm_status_check_cmdb = host_detail['vm_status_check_cmdb']
        cmdb_stat_check_agp = host_detail['cmdb_stat_check_agp']
        nas_validate = host_detail['nas_validate']
        fqdn = host_detail['fqdn']
        filter_domain = host_detail['filter_domain']
        instanceid=host_detail['instanceid']
        deco_date = host_detail.get('deco_date', 'F')
        idempotent_obj = {}
        idempotent_obj['hostname'] = hostname
        idempotent_obj['os'] = os
        idempotent_obj['os_fetch_status'] = os_fetch_status
        idempotent_obj['app_validation'] = application_validation
        idempotent_obj['network'] = network
        idempotent_obj['sanstorage'] = sanstorage
        idempotent_obj['nasstorage'] = nasstorage
        idempotent_obj['backup'] = backup
        idempotent_obj['dns'] = dns
        idempotent_obj['vm_poweroff'] = vm_poweroff
        idempotent_obj['vm_delete'] = vm_delete
        idempotent_obj['cmdb'] = cmdb
        idempotent_obj['vm_poweroff_before_gp'] = vm_poweroff_before_gp
        idempotent_obj['vm_status_check_cmdb'] = vm_status_check_cmdb
        idempotent_obj['cmdb_stat_check_agp'] = cmdb_stat_check_agp
        idempotent_obj['nas_validate'] = nas_validate
        idempotent_obj['fqdn'] = fqdn
        idempotent_obj['filter_domain'] = filter_domain
        idempotent_obj['instanceid'] = instanceid
        idempotent_obj['deco_date'] = deco_date
        
    else: 
        new_ent = {'RowKey':hostname,'PartitionKey':hostname[:2],'os':'F','os_fetch_status':'F','app_validation':'F','network':'F',
                    'sanstorage':'F','nasstorage':'F','backup':'F','dns':'F','vm_poweroff':'F','vm_delete':'F','cmdb':'F',
                    'vm_poweroff_before_gp':'F','vm_status_check_cmdb':'F','cmdb_stat_check_agp':'F',
                    'nas_validate':'F','fqdn':'F','filter_domain':'F','instanceid':'F','deco_date':'F'} 
        temp = service.create_entity(new_ent)
            
        idempotent_obj = {}
        idempotent_obj['hostname'] = hostname
        idempotent_obj['os'] = 'F'
        idempotent_obj['os_fetch_status'] = 'F'
        idempotent_obj['app_validation'] = 'F'
        idempotent_obj['network'] = 'F'
        idempotent_obj['sanstorage'] = 'F'
        idempotent_obj['nasstorage'] ='F'
        idempotent_obj['backup'] = 'F'
        idempotent_obj['dns'] = 'F'
        idempotent_obj['vm_poweroff'] = 'F'
        idempotent_obj['vm_delete'] = 'F'
        idempotent_obj['cmdb'] = 'F'
        idempotent_obj['vm_poweroff_before_gp'] = 'F'
        idempotent_obj['vm_status_check_cmdb'] = 'F'
        idempotent_obj['cmdb_stat_check_agp'] = 'F'
        idempotent_obj['nas_validate'] = 'F'
        idempotent_obj['fqdn'] = 'F'
        idempotent_obj['filter_domain'] = 'F'
        idempotent_obj['instanceid'] = 'F'
        idempotent_obj['deco_date'] = 'F'
    
    return idempotent_obj


def run_module():

    table_name = "hostDetails"
    fields = {
        "connection_string":{"required":True,"type":"str"},
        "hostname":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_entity(connection_string= module.params["connection_string"],
                                  table_name= table_name,
                                  hostname= module.params["hostname"])
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