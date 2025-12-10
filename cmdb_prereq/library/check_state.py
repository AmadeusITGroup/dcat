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
    if str(dataframe['cr'].item()) == str(cr):
        app = dataframe['app_tr_status'].item()
        owner = dataframe['owner_tr_status'].item()
        if (app == 'open' and owner == 'open'):
            tr_obj = {}
            ci = dataframe['ci'].item()
            cr = dataframe['cr'].item()
            app_tr = dataframe['app_tr'].item()
            owner_tr = dataframe['owner_tr'].item()
            tr_obj['ci'] = ci
            tr_obj['cr'] = cr
            tr_obj['app_tr'] = app_tr
            tr_obj['owner_tr'] = owner_tr
            tr_obj['app_tr_status'] = app
            tr_obj['owner_tr_status'] = owner
            return tr_obj
        elif(app == 'open' or owner == 'open'):
           tr_obj = {}
           ci = dataframe['ci'].item()
           cr = dataframe['cr'].item()
           app_tr = dataframe['app_tr'].item()
           owner_tr = dataframe['owner_tr'].item()
           tr_obj['ci'] = ci
           tr_obj['cr'] = cr
           tr_obj['app_tr'] = app_tr
           tr_obj['owner_tr'] = owner_tr
           tr_obj['app_tr_status'] = app
           tr_obj['owner_tr_status'] = owner
           return tr_obj
        else:
            tr_obj = "NA"
            return tr_obj

 
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
        returnvalue["status"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
