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
        description: VM name
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


def fetch_details(vmname,synergon_api):
    url = "https://"+ synergon_api +"/v1/vms/?expand=host&offset=0&limit=10&name=" + vmname
    httprequest = Request(url, headers = {"Accept":"application/json"})
    with urlopen(httprequest) as response:
        result = response.read().decode()
        r_dict = json.loads(result)["data"]
        if len(r_dict)==1:
            v_cen = r_dict[0]
            vcen_ter = v_cen['vcenter']
        else:
            vcen_ter = "duplicate entries or server doesnt exist in vcenter."
        return vcen_ter
def run_module():
    fields = {
         "vmname":{"required":True, "type":"str"},
         "synergon_api":{"required":True, "type":"str"},
         "instance_id_vm":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        vcenter = fetch_details(vmname = module.params["vmname"],
                                synergon_api = module.params["synergon_api"]
                                )
        #print("this is executed")
        if "Exception" in vcenter or "duplicate entries" in vcenter:
            returnvalue["vcenter"] = ""
            returnvalue["msg"] = vcenter + module.params["vmname"]
            module.exit_json(**returnvalue)

        else:
            returnvalue["vcenter"] = vcenter
            returnvalue["msg"] = "Successfully fetched Vcenter name for " + module.params["vmname"]
            module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "Exception occurred while fetching the vcenter details.Kindly check. " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
