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
msg:
    description: Status message from module.
    type: str
    returned: always
    sample: 'Successfuly fetched Vcenter name.'
vcenter:
    description: Vcenter name fetched from module.
    type: str
    returned: always
    sample: '' 

'''
def fetch_details(vmname,synergon_api,instance_id_vm):
    try:
        url = "https://"+ synergon_api +"/v1/vms/?expand=host&offset=0&limit=10&name=" + vmname
        httprequest = Request(url, headers = {"Accept":"application/json"})
        with urlopen(httprequest) as response:
            s_data = response.read().decode()
            r_dict = json.loads(s_data)["data"]
        if len(r_dict)==0:
            vcenter= "Unable to find vcenter of the vm from synergon .check the input vm "
            uuid_vm=""

        elif len(r_dict)==1:
            vcenter= r_dict[0]['vcenter']
            uuid_vm= ""
        else:
            result = []
            result_uuid = []
            result_unable = []
            for item in r_dict:
                if 'ci' in item and 'ciInstanceId' in item['ci']:
                    ci_instance_id = item['ci']['ciInstanceId']
                    if ci_instance_id == instance_id_vm:
                        result.append(item['vcenter'])
                        result_uuid.append(item['uuid'])
                        #print(item['vcenter'])
                    else:
                        vcenter_v= "Unable to find Vcenter name as InstanceId doesnt match "
                        result_unable.append(vcenter_v)
                else:
                    vcenter_v="Unable to find InstanceId of the vm from synergon "
                    result_unable.append(vcenter_v)
            if len(result) == 0 and len(result_unable) != 0:
                vcenter = "duplicate entries exist and InstanceId doesnt match or unable to find InstanceId of the vm from synergon "
                uuid_vm=""
            elif len(result) == 1 :
                vcenter = result[0]
                uuid_vm= result_uuid[0]
            else:
                vcenter = "duplicate entries with same instance id for the vm  "
                uuid_vm=""
        return vcenter,uuid_vm
        #print(vcenter)
    except Exception as err: # pylint: disable=broad-except
        vcenter = "Exception occurred: "+str(err)
        uuid_vm=""
        return vcenter,uuid_vm
def run_module():
    fields = {
         "vmname":{"required":True, "type":"str"},
         "synergon_api":{"required":True, "type":"str"},
         "instance_id_vm":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        vcenter_res = fetch_details(vmname = module.params["vmname"],synergon_api = module.params["synergon_api"],instance_id_vm = module.params["instance_id_vm"] )
        vcenter =vcenter_res[0]
        uuid_res=vcenter_res[1]
        if "Unable to find" in vcenter or "Exception" in vcenter or "duplicate entries" in vcenter:
            returnvalue["vcenter"] = ""
            returnvalue["msg"] = vcenter + module.params["vmname"]
            module.exit_json(**returnvalue)
        else:
            returnvalue["vcenter"] = vcenter
            returnvalue["uuid_vm"] = uuid_res
            returnvalue["msg"] = "Successfully fetched Vcenter name for " + module.params["vmname"]
            module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["vcenter"] = ""
        returnvalue["msg"] = "Exception occurred while fetching the vcenter details.Kindly check. " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
