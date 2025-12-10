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
    closing_comment: 
       description: Cloaing Task record with partial implment comment
       required: true
       type: list             
       
    
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
            closing_comment: "{{ closing_comment }}"
          register: close_partial_implement
          delegate_to: localhost
'''
def problem_tr(win_url,username,password,ptr_title,tr_map,assignee_group,ptr_logs,winaproach_category,ptr_system):
    url="https://"+ win_url +"/aproach-api/v1.0/problemtrackingrecords/"
    headers={"Content-Type":"application/json"}
    data1={"operation": "ptr_simple_create","problemTrackingRecord": {"normalFields": {"Severity" :"3","Title":ptr_title,"Location":"BLR","AsysCategory":winaproach_category,"ActiveSystem":ptr_system,"UrgencyCode":"Y","TRReference":tr_map,"AssigneeGroup":assignee_group},"StatusText" :{"text":ptr_logs}}}
    result=requests.post(url,auth=(username, password),data=json.dumps(data1),headers=headers)
    time.sleep(10)
    id = result.json()['recordId']
    return id

def main():
    returnvalue = {}
    fields = {
        "win_url":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "ptr_title":{"required":True, "type":"str"},
        "tr_map":{"required":True, "type":"str"},
        "assignee_group":{"required":True, "type":"str"},
        "ptr_logs":{"required":True, "type":"str"},
        "winaproach_category":{"required":True, "type":"str"},
        "ptr_system":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = problem_tr(module.params["win_url"],
                            module.params["username"],
                            module.params["password"],
                            module.params["ptr_title"],
                            module.params["tr_map"],
                            module.params["assignee_group"],
                            module.params["ptr_logs"],
                            module.params["winaproach_category"],
                            module.params["ptr_system"])
        returnvalue["id"] = status
        returnvalue["msg"] = "Successfully created PTR"
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "Exception while creating PTR " + str(err)
        module.exit_json(**returnvalue)


if __name__ == '__main__':
    main()
