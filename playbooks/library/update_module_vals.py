from io import StringIO
import warnings
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
import requests
pd.options.mode.chained_assignment = None
warnings.simplefilter(action='ignore', category=FutureWarning)

DOCUMENTATION = r'''
---
module: Update module results to reference point to acheive idempotency logic

description: Update module results to reference point to acheive idempotency logic.

version_added: "1.0.0"

options:
    hostname:
        description: Hostname of the DECO server.
        required: true
        type: str
    module_name:
        description: module name of the DECO process.
        required: true
        type: str
    status:
        description: status of the module eg> (True or False)
        required: true
        type: str

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_module_vals:
            hostname: "{{hostname}}"
            module_name: "{{module_name}}"
            status: "{{ status }}"
          register: update_status
          delegate_to: localhost
'''


def write_data(hostname,module_name,result,artifacts_user,
               artifacts_password,state_file_url,lookup_file):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file
    username= artifacts_user
    pwd= artifacts_password
    session.auth = (username, pwd)
    response = session.get(url)
    data = response.text
    data_frame = pd.read_csv(StringIO(data))
    if data_frame['hostname'].str.contains(hostname).any():
        data_frame[module_name][data_frame['hostname']==hostname] = result
        auth=(username,pwd)
        response = requests.put(url, auth=auth, data=data_frame.to_csv(index=False))
        status = module_name+" : status updated for host " + hostname
    else:
        status = module_name+" not found and unable to update for host "+ hostname
    return status


def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "module_name":{"required":True, "type":"str"},
        "status":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str","no_log":True},
        "artifacts_password":{"required":True, "type":"str","no_log":True},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["hostname"],
                            module.params["module_name"],
                            module.params["status"],
                            module.params["artifacts_user"],
                            module.params["artifacts_password"],
                            module.params["state_file_url"],
                            module.params["lookup_file"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
