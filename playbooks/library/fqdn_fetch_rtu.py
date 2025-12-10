from ansible.module_utils.basic import AnsibleModule
import pandas as pd
pd.set_option('display.expand_frame_repr', False)

DOCUMENTATION = r'''
---
module: Fetch CMDB RTU SERVER STATUS
description: This module Queries Status of the server for fetching fqdn
version_added: "1.0.0"

options:
    host:
        description: Server ready for decommisioning
        required: true
        type: str
    cmdb_rtu:
        description: cmdb rtu server
        required: true
        type: str
author:
    - Leethu T.L (@ltl)
'''
EXAMPLES = r'''
          
        - name: "Test CMDB custom module from rtu status check"
          cmdb_fetch_rtu:
            host: '{{ inventory_hostname | lower }}'  
            cmdb_rtu: "{{ cmdb_rtu }}"
          delegate_to: localhost
'''
# host="vmdecovt005"
# cmdb_rtu=""{{CMDB_URL}}""

def fetch_rtu_fqdn(host,cmdb_rtu):
    idem = {}
    url = "https://"+cmdb_rtu+"/rtu/?serverName="+host.lower()
    data_frame = pd.read_json(url)
    if data_frame.empty or host=="":
        msg ="No Entry Available for host in RTU"
        idem[msg] = msg
        idem['fqdn'] =' '
        idem['ip'] = ' '
    else:
        data=data_frame.loc[data_frame['serverName'] == host]
        if data.empty:
            msg = "No Entry Available for host: "+ host
            idem [msg] = msg
            idem['fqdn'] =' '
            idem['ip'] = ' '
        else:
            if len(data) == 1:
                fqdn_info = data['serverFQDN'].item()
                ip_info = data['serverIpInformation'].item()
                idem['fqdn'] = fqdn_info
                idem['ip'] = ip_info
            else:
                fqdn = data.iloc[0]['serverFQDN']     
                ip = data.iloc[0]['serverIpInformation'] 
                idem['fqdn'] = fqdn
                idem['ip'] = ip
        
    return idem

# print(fetch_rtu_fqdn(host,cmdb_rtu))

def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"str"},
         "cmdb_rtu":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        vm_status = fetch_rtu_fqdn(module.params["host"],module.params["cmdb_rtu"])
        returnvalue["rtu_status_fqdn"] = vm_status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["rtu_status_fqdn"] = "Exception occurred" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
