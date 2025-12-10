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
        cmdb_fetch = host_detail['cmdb_fetch']
        esxi_type = host_detail['esxi_type']
        enclosure_name = host_detail['enclosure_name']
        fqdn_info = host_detail['fqdn_info']
        vcenter_info = host_detail['vcenter_info']
        oneview_xclarity_info = host_detail['oneview_xclarity_info']
        cmdb_dup_check= host_detail['cmdb_dup_check']
        server_info = host_detail['server_info']
        san_info_fetch = host_detail['san_info_fetch']
        backup = host_detail['backup']
        nvme_cleanup = host_detail['nvme_cleanup']
        ilo_reset = host_detail['ilo_reset']
        server_shutdown = host_detail['server_shutdown']
        ipam_cleanup = host_detail['ipam_cleanup']
        network_cleanup = host_detail['network_cleanup']
        oneview_xclarity_removal = host_detail['oneview_xclarity_removal']
        vcenter_cleanup = host_detail['vcenter_cleanup']
        enclosure_check = host_detail['enclosure_check']
        dcm = host_detail['dcm']
        firewall = host_detail['firewall']
        san_cleanup = host_detail['san_cleanup']
        cmdb_update = host_detail['cmdb_update']
        deco_date = host_detail['deco_date']

        idempotent_obj['cmdb_fetch'] = cmdb_fetch
        idempotent_obj['esxi_type'] = esxi_type
        idempotent_obj['enclosure_name'] = enclosure_name
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['vcenter_info'] = vcenter_info
        idempotent_obj['oneview_xclarity_info'] = oneview_xclarity_info
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['server_info'] = server_info
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['backup'] = backup
        idempotent_obj['nvme_cleanup'] = nvme_cleanup
        idempotent_obj['ilo_reset'] = ilo_reset
        idempotent_obj['server_shutdown'] = server_shutdown
        idempotent_obj['ipam_cleanup'] = ipam_cleanup
        idempotent_obj['network_cleanup'] = network_cleanup
        idempotent_obj['oneview_xclarity_removal'] = oneview_xclarity_removal
        idempotent_obj['vcenter_cleanup'] = vcenter_cleanup
        idempotent_obj['enclosure_check'] = enclosure_check
        idempotent_obj['dcm'] = dcm
        idempotent_obj['firewall'] = firewall
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['deco_date'] = deco_date
    else:
        new_entry = {'RowKey':hostname,'PartitionKey':hostname[:2],'cmdb_fetch':'F','esxi_type':'F','enclosure_name':'F',
                        'fqdn_info':'F','vcenter_info':'F','oneview_xclarity_info':'F','cmdb_dup_check':'F','server_info':'F',
                        'san_info_fetch':'F','backup':'F','nvme_cleanup':'F','ilo_reset':'F','server_shutdown':'F',
                        'ipam_cleanup':'F','network_cleanup':'F','oneview_xclarity_removal':'F','vcenter_cleanup':'F',
                        'enclosure_check':'F','dcm':'F','firewall':'F','san_cleanup':'F','cmdb_update':'F','deco_date' : 'F'}
        
        temp = service.create_entity(new_entry)

        idempotent_obj = {}
        hostname=hostname
        cmdb_fetch='F'
        esxi_type='F'
        enclosure_name='F'
        fqdn_info='F'
        vcenter_info='F'
        oneview_xclarity_info='F'
        cmdb_dup_check='F'
        server_info='F'
        san_info_fetch='F'
        backup='F'
        nvme_cleanup='F'
        ilo_reset='F'
        server_shutdown='F'
        ipam_cleanup='F'
        network_cleanup='F'
        oneview_xclarity_removal='F'
        vcenter_cleanup='F'
        enclosure_check='F'
        dcm='F'
        firewall='F'
        san_cleanup='F'
        cmdb_update='F'
        deco_date='F'
        
        idempotent_obj['hostname'] = hostname
        idempotent_obj['cmdb_fetch'] = cmdb_fetch
        idempotent_obj['esxi_type'] = esxi_type
        idempotent_obj['enclosure_name'] = enclosure_name
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['vcenter_info'] = vcenter_info
        idempotent_obj['oneview_xclarity_info'] = oneview_xclarity_info
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['server_info'] = server_info
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['backup'] = backup
        idempotent_obj['nvme_cleanup'] = nvme_cleanup
        idempotent_obj['ilo_reset'] = ilo_reset
        idempotent_obj['server_shutdown'] = server_shutdown
        idempotent_obj['ipam_cleanup'] = ipam_cleanup
        idempotent_obj['network_cleanup'] = network_cleanup
        idempotent_obj['oneview_xclarity_removal'] = oneview_xclarity_removal
        idempotent_obj['vcenter_cleanup'] = vcenter_cleanup
        idempotent_obj['enclosure_check'] = enclosure_check
        idempotent_obj['dcm'] = dcm
        idempotent_obj['firewall'] = firewall
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['deco_date'] = deco_date
    return idempotent_obj
    

def main():
    returnvalue = {}
    
    table_name = "EsxiServerDetails"
    
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