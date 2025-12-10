import json
import ast
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION='''
    This module collects the JSON input and parse the information and creates host inventory file at runtime
    
'''

def run_module():
    returnvalue = {}
    try:
        fields = {
           "host_info":{"required":True,"Type":"list"}
        }
        module = AnsibleModule(argument_spec = fields)
        host_list = []
        info = module.params["host_info"]
        val = json.dumps(info)
        value = ast.literal_eval(val)
        result = json.loads(value)
        for val in result:
            host_list.append(val['hosts'])
        returnvalue["host_list"] = host_list
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.exit_json(**returnvalue)

if __name__=='__main__':
    run_module()
