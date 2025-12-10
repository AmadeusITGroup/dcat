from ansible.module_utils.basic import AnsibleModule
import pandas as pd
pd.set_option('display.expand_frame_repr', False)

DOCUMENTATION = r'''
---
module: Fetch FQDN

description: This module Queries the RTU  application URL to FQDN of the target host.

version_added: "1.0.0"

options:
    host:
        description: Server on which application validation to be performed.
        required: true
        type: str
author:
    - Prashanth k (@ppk1)
'''

EXAMPLES = r'''
      - name: "fetch FQDN from CMDB RTU"
          get_fqdn:
            host: "{{inventory_hostname}}"
          register: fqdn_info
          delegate_to: localhost
'''

def fetch_fqdn(host,cmdb_rtu):
    url = "https://"+cmdb_rtu+"/rtu/?serverName="+host
    try:
        data_frame = pd.read_json(url)
        fqdn= data_frame['serverFQDN'][0]
        if fqdn:
            return fqdn
        else:
            return "NA"
    except Exception as err:
        return "NA"

def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"str"},
         "cmdb_rtu":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        fqdn_status = fetch_fqdn(module.params["host"],module.params["cmdb_rtu"])
        returnvalue["status"] = fqdn_status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
