#!/usr/bin/env python3

import requests
import json
from ansible.module_utils.basic import AnsibleModule


# Function to update PTR status
def update_ptr_status(record_id, win_target, username, password, status_text):

    session = requests.Session()
    url="https://"+win_target+"/aproach-api/v1.0/problemtrackingrecords/"+record_id
    session.auth = (username, password)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "operation": "ptr_solved_to_closed",
        "problemTrackingRecord": {
            "StatusText": {
                "text": "API Solved to Closed"
            }
        }
    }

    response = session.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return (f"Record {record_id} updated successfully: {response.json()}")
    else:
        return (f"[Exception] Failed to update record {record_id}: {response.status_code}, {response.text}")


def run_module():

    fields = {
        "record_id": {"required":True, type:"str"},
        "win_target":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}
    }

    status_text = 'Closed'

    module = AnsibleModule(argument_spec = fields)
    returnvalue = {
        "msg":"",
        "closed":False
    }

    try:
        updated_status = update_ptr_status(module.params["record_id"], module.params["win_target"], 
                                            module.params["username"], module.params["password"], status_text)
        
        if updated_status:
            returnvalue["msg"] = updated_status
            returnvalue["closed"] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["msg"] = updated_status
            module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = f"[Exception] "+str(err)
        returnvalue["closed"] = False
        module.fail_json(**returnvalue)

if __name__=='__main__':
    run_module()
    