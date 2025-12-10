import ast
import requests
from ansible.module_utils.basic import AnsibleModule
# from update_TR  import update_tr

DOCUMENTATION = '''
---
module: getserverdetails
short_description: Fetch the VM details from CMDB
'''''
# Fetching VM details
def fetch_cmdb(param,cmdb_api):
    response_api = requests.get('https://'+cmdb_api+'/rtu/', params=param)
    if response_api.status_code == 200:
        con = response_api.content
        result = con.decode("UTF-8")
        result = ast.literal_eval(result)
        if result:
            result = result[0]
        else:
            result = 0
    return result
def getserverdetails():
    fields = {
        "vmname": {"required": True, "type": "str"},
        "cmdb_api": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)
    returnvalue = {}
    if module.params["vmname"] == "":
        returnvalue["msg"] = "App argument cannot be empty"
        module.fail_json(**returnvalue)
    vm_domain = module.params["vmname"]
    vm_server = vm_domain.split(".")
    cmdb_api= module.params["cmdb_api"]
    param = {'serverName': vm_server}
    vmdata = fetch_cmdb(param,cmdb_api)
    if vmdata:
        vmtype = vmdata['serverIsVirtual']
        returnvalue["v_type"] = vmtype

    else:
        returnvalue["v_type"] = 0
    module.exit_json(**returnvalue)

if __name__ == '__main__':
    getserverdetails()
