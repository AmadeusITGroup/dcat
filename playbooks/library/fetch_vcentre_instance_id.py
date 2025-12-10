from urllib.request import urlopen, Request
import json
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: fetch_vcentre

description: Fetching instance id when a vmname is available

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
        synergon_api: "{{SYNERGON_INSTANCE}}" 
        
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
ci_instance_id:
    description: ci instance id fetched from module.
    type: str
    returned: always
    sample: '' 

'''
def fetch_details(vmname,synergon_api):
    try:
        url = "https://"+ synergon_api +"/v1/vms/?expand=host&offset=0&limit=10&name=" + vmname
        httprequest = Request(url, headers = {"Accept":"application/json"})
        with urlopen(httprequest) as response:
            s_data = response.read().decode()
            r_dict = json.loads(s_data)["data"]
        if len(r_dict)==0:
            ci_instance_id="Unable to fetch instance id as there is no data in synergon"

        elif len(r_dict)==1:
            ci_instance_id = r_dict[0]['ci']['ciInstanceId']
        else:
            ci_instance_id="multiple instances present in synergon for the server"
        return ci_instance_id

    except Exception as err: # pylint: disable=broad-except
        ci_instance_id = "Exception occurred: "+str(err)
        return ci_instance_id

def run_module():
    fields = {
         "vmname":{"required":True, "type":"str"},
         "synergon_api":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        ci_instance_id = fetch_details(vmname = module.params["vmname"],synergon_api = module.params["synergon_api"])
        if "Unable to" in ci_instance_id or "Exception" in ci_instance_id or "multiple" in ci_instance_id:
            returnvalue["ci_instance_id"] = ci_instance_id
            module.exit_json(**returnvalue)
        else:
            returnvalue["ci_instance_id"] = ci_instance_id
            module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["ci_instance_id"] = "Exception occurred while fetching instance id details.Kindly check. " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
