'''
 State File updation custom module
'''
from azure.data.tables import TableClient, UpdateMode
import time, configparser
from io import StringIO
import warnings
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
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

        hostname = host_detail['RowKey']
        partition_key = host_detail['PartitionKey']

        idempotent_obj = {}
        cmdb_dup_check= host_detail['cmdb_dup_check']
        fqdn_info= host_detail['fqdn_info']
        info = host_detail['info']
        poweron = host_detail['poweron']
        cmdb_fetch_bgp = host_detail['cmdb_fetch_bgp']
        san_info_fetch = host_detail['san_info_fetch']
        cmdb_fetch_agp = host_detail['cmdb_fetch_agp']
        backup = host_detail['backup']
        network = host_detail['network']
        dns = host_detail['dns']
        ilo = host_detail['ilo']
        shutdown = host_detail['shutdown']
        shutdown_bgp = host_detail['shutdown_bgp']
        san_cleanup = host_detail['san_cleanup']
        nvme_cleanup = host_detail['nvme_cleanup']
        cmdb_update = host_detail['cmdb_update']
        serial = host_detail['serial']
        ilo_reconfig = host_detail['ilo_reconfig']
        deco_date = host_detail['deco_date']
        idempotent_obj['ilo_reconfig'] = ilo_reconfig
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['info'] = info
        idempotent_obj['cmdb_fetch_bgp'] = cmdb_fetch_bgp
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['cmdb_fetch_agp'] = cmdb_fetch_agp
        idempotent_obj['backup'] = backup
        idempotent_obj['network'] = network
        idempotent_obj['dns'] = dns
        idempotent_obj['ilo'] = ilo
        idempotent_obj['shutdown'] = shutdown
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['nvme_cleanup'] = nvme_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['poweron'] = poweron
        idempotent_obj['serial'] = serial
        idempotent_obj['shutdown_bgp'] = shutdown_bgp
        idempotent_obj['deco_date'] = deco_date
    else:
        new_entry = {'RowKey':hostname,'PartitionKey':hostname[:2],'ilo_reconfig':'F','cmdb_dup_check':'F','fqdn_info':'F','info':'F',
                     'cmdb_fetch_bgp':'F','san_info_fetch':'F','cmdb_fetch_agp':'F',
                     'backup':'F','network':'F','poweron':'F',
                     'dns':'F',
                     'ilo':'F','shutdown':'F',
                     'san_cleanup':'F','nvme_cleanup':'F','cmdb_update':'F','serial':'F','shutdown_bgp':'F','deco_date' : 'F'}
        
        temp = service.create_entity(new_entry)

        idempotent_obj = {}
        hostname=hostname
        cmdb_dup_check='F'
        fqdn_info='F'
        info='F'
        cmdb_fetch_bgp='F'
        san_info_fetch='F'
        cmdb_fetch_agp='F'
        backup='F'
        network='F'
        dns='F'
        ilo='F'
        shutdown='F'
        san_cleanup='F'
        nvme_cleanup='F'
        cmdb_update='F'
        poweron='F'
        serial='F'
        shutdown_bgp='F'
        ilo_reconfig='F'
        deco_date ='F'
        idempotent_obj['hostname'] = hostname
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['info'] = info
        idempotent_obj['cmdb_fetch_bgp'] = cmdb_fetch_bgp
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['cmdb_fetch_agp'] = cmdb_fetch_agp
        idempotent_obj['backup'] = backup
        idempotent_obj['network'] = network
        idempotent_obj['dns'] = dns
        idempotent_obj['ilo'] = ilo
        idempotent_obj['shutdown'] = shutdown
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['nvme_cleanup'] = nvme_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['poweron'] = poweron
        idempotent_obj['serial'] = serial
        idempotent_obj['shutdown_bgp'] = shutdown_bgp
        idempotent_obj['ilo_reconfig'] = ilo_reconfig
        idempotent_obj['deco_date'] = deco_date
    return idempotent_obj
    

def main():
    returnvalue = {}
    
    table_name = "PhysicalServerDetails"
    
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
        returnvalue["module_update"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()