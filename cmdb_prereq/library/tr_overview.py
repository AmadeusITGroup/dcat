import warnings
import time
import json
from ansible.module_utils.basic import AnsibleModule
import requests
warnings.simplefilter(action='ignore', category=FutureWarning)

DOCUMENTATION = r'''
---
module: Closing the TR with status as Partially implemented

description: Closing the TR with status as Partially implemented

version_added: "1.0.0"

options:
    username:
        description: Username for the template creation API call.
        required: true
        type: str
    password:
        description: Password for the template creation API call.
        required: true
        type: str
    win_url:
        description: Win@proach url for partial implmentation
        required: true
        type: str
    task_id:
        description: the task record ID
        required: true
        type: str
    prob_id: 
       description: Problem Task Record of the TR needs to be updated.
       required: true
       type: str             
       
    
author:
    - Thineshumar R (@thr)
'''

EXAMPLES = r'''
- name: Implementation partial that is closing the implementation as partial
          tr_partial_close:
            username: "{{username}}"
            password: "{{password}}"
            win_url: "{{ win_url }}"
            task_id: "{{ task_id }}"
            prob_id: "{{ prob_id }}"
          register: close_partial_implement
          delegate_to: localhost
'''
def tr_overview(win_url,username,password,task_id,prob_id):
    url="https://"+ win_url +"/aproach-api/v1.0/taskrecords/"+ task_id
    headers={"Content-Type":"application/json"}
    data1={"operation": "tr_update_overview",
            "taskRecord": {"Overview": {"text": "!PTR : "+ prob_id}}}
    result=requests.put(url,auth=(username, password),data=json.dumps(data1),headers=headers)
    time.sleep(10)
    status = result.json()
    return status

def main():
    returnvalue = {}
    fields = {
        "win_url":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "task_id":{"required":True, "type":"str"},
        "prob_id":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = tr_overview(module.params["win_url"],
                            module.params["username"],
                            module.params["password"],
                            module.params["task_id"],
                            module.params["prob_id"])
        returnvalue["status"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Error"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
