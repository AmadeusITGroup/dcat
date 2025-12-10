from urllib.request import urlopen, Request
import json
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: fetch_vcentre

description: Fetching Vcenter name when a vmname is available

version_added: "1.0.0"

options:
    vmname:
        description: VM name.
        required: true
        type: str

    synergon_api:
        description: API URL.
        required: true
        type: str     
    
author:
    - Leethu T.L (@pltl)
'''

EXAMPLES = r'''
# Module usage example 
- name: "Test custom module"
      fetch_vcentre:
        vmname: "vmdecoprj01"
        synergon_api: "{{SYNERGON_INSTANCE}}" #prod instance is taken currently
        
'''

RETURN = r'''
# Module return values
vmname:
    description: Name of VM passed into module.
    type: str
    returned: always
    sample: 'vmdecoprj01'
changed:
    description: Boolean indicating if the module made changes to the target or delegated host.
    type: bool
    returned: always
    sample: false
msg:
    description: Status message from module.
    type: str
    returned: always
    sample: 'Successfuly fetched Vcenter name.'
vcenter:
    description: Vcenter name fetched from module.
    type: str
    returned: always
    sample: '' ###Need to test with CNB instance

'''


def fetch_fqdn(vmname,synergon_api):
    url = "https://"+ synergon_api +"/v1/vms/?expand=host&offset=0&limit=10&name=" + vmname
    httprequest = Request(url, headers = {"Accept":"application/json"})

    with urlopen(httprequest) as response:

        s_data= response.read().decode()
        r_dict = json.loads(s_data)["data"]
        x_data = r_dict[0]
        fqdn = x_data['ci']['fqdn']
        return fqdn


def run_module():

    fields = {
         "vmname":{"required":True, "type":"str"},
         "synergon_api":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        fqdn = fetch_fqdn(vmname = module.params["vmname"],synergon_api = module.params["synergon_api"] )
        returnvalue["host_fqdn"] = fqdn
        returnvalue["msg"] = "[INFO] Successfully fetched FQDN for " + module.params["vmname"]
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["host_fqdn"] = ""
        returnvalue["msg"] = "[ERROR] Exception occurred while fetching the vcenter for host: "+ module.params["vmname"] +" details with ERROR: " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
