'''
 State File updation custom module
'''
import time
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

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_ref:
            hostname: "{{hostname}}"
          register: update_status
          delegate_to: localhost
'''

def write_data(cr,artifacts_user,artifacts_password,state_file_url,lookup_file):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file
    session.auth = (artifacts_user, artifacts_password)
    response = session.get(url)
    data = response.text
    dataframe = pd.read_csv(StringIO(data))
    if dataframe['cr'].astype(str).str.contains(cr).any():
        #print("already Exists and grepping existing value")
        loc = dataframe.loc[dataframe['cr'].astype(str).str.contains(cr)]
        idempotent_obj = {}
        app_tr = loc['app_tr'].item()
        owner_tr = loc['owner_tr'].item()
        ci = loc['ci'].item()
        app_tr_status = loc['app_tr_status'].item()
        owner_tr_status = loc['owner_tr_status'].item()
        idempotent_obj['app_tr'] = app_tr
        idempotent_obj['owner_tr'] = owner_tr
        idempotent_obj['app_tr_status'] = app_tr_status
        idempotent_obj['owner_tr_status'] = owner_tr_status
        idempotent_obj['ci'] = ci
    else:
        new_entry = {'cr':cr,'app_tr':'F','owner_tr':'F',
                     'app_tr_status':'F','owner_tr_status':'F','ci':'F'}
        dataframe = dataframe.append(new_entry, ignore_index=True)
        time.sleep(5)
        auth=(artifacts_user,artifacts_password)
        response = requests.put(url, auth=auth, data=dataframe.to_csv(index=False))
        idempotent_obj = {}
        cr=cr
        app_tr='F'
        owner_tr='F'
        app_tr_status='F'
        owner_tr_status='F'
        ci='F'
        idempotent_obj['app_tr'] = app_tr
        idempotent_obj['owner_tr'] = owner_tr
        idempotent_obj['app_tr_status'] = app_tr_status
        idempotent_obj['owner_tr_status'] = owner_tr_status
        idempotent_obj['ci'] = ci
    return idempotent_obj
    
def main():
    returnvalue = {}
    fields = {
        "cr":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str"},
        "artifacts_password":{"required":True, "type":"str"},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["cr"],module.params["artifacts_user"],
                            module.params["artifacts_password"],module.params["state_file_url"],
                            module.params["lookup_file"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
