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

def write_data(ci,cr,artifacts_user,artifacts_password,state_file_url,lookup_file,ritm_number,requester_name,requester_group,retention_days):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file
    session.auth = (artifacts_user, artifacts_password)
    response = session.get(url)
    data = response.text
    dataframe = pd.read_csv(StringIO(data))
    # if dataframe['ci'].astype(str).str.contains(ci).any():
    #     loc = dataframe.loc[dataframe['ci'].astype(str).str.contains(ci)]
    if dataframe['ci'].str.contains(ci).any():
        #print("already Exists and grepping existing value")
        loc = dataframe.loc[dataframe['ci'] == ci]    
        idempotent_obj = {}
        app_tr = loc['app_tr'].item()
        owner_tr = loc['owner_tr'].item()
        cr = loc['cr'].item()
        app_tr_status = loc['app_tr_status'].item()
        owner_tr_status = loc['owner_tr_status'].item()
        ritm_number = loc['ritm_number'].item()
        requester_name = loc['requester_name'].item()
        requester_group = loc['requester_group'].item()
        retention_days = loc['retention_days'].item()
        cmdb = loc['cmdb'].item()
        idempotent_obj['app_tr'] = app_tr
        idempotent_obj['owner_tr'] = owner_tr
        idempotent_obj['cr'] = cr
        idempotent_obj['app_tr_status'] = app_tr_status
        idempotent_obj['owner_tr_status'] = owner_tr_status
        idempotent_obj['ritm_number'] = ritm_number
        idempotent_obj['requester_name'] = requester_name
        idempotent_obj['requester_group'] = requester_group
        idempotent_obj['retention_days'] = retention_days
        idempotent_obj['cmdb'] = cmdb                
    else:
        new_entry = {'ci':ci,'app_tr':0,'owner_tr':0,
                     'cr':cr,'app_tr_status':'F','owner_tr_status':'F','ritm_number':ritm_number,'requester_name':requester_name,
                     'requester_group':requester_group,'retention_days':retention_days,'cmdb':'F'}
        dataframe = dataframe.append(new_entry, ignore_index=True)
        time.sleep(5)
        auth=(artifacts_user,artifacts_password)
        response = requests.put(url, auth=auth, data=dataframe.to_csv(index=False))
        idempotent_obj = {}
        ci=ci
        app_tr=0
        owner_tr=0
        cr=cr        
        app_tr_status='F'
        owner_tr_status='F'        
        ritm_number=ritm_number
        requester_name=requester_name
        requester_group=requester_group
        retention_days=retention_days
        cmdb='F'
        idempotent_obj['app_tr'] = app_tr
        idempotent_obj['owner_tr'] = owner_tr
        idempotent_obj['cr'] = cr        
        idempotent_obj['app_tr_status'] = app_tr_status
        idempotent_obj['owner_tr_status'] = owner_tr_status
        idempotent_obj['ritm_number'] = ritm_number
        idempotent_obj['requester_name'] = requester_name
        idempotent_obj['requester_group'] = requester_group
        idempotent_obj['retention_days'] = retention_days
        idempotent_obj['cmdb'] = cmdb
    return idempotent_obj

def main():
    returnvalue = {}
    fields = {
        "ci":{"required":True, "type":"str"},
        "cr":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str"},
        "artifacts_password":{"required":True, "type":"str"},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file": {"required":True, "type":"str"},
        "ritm_number": {"required":True, "type": "str"},
        "requester_name": {"required":True, "type": "str"},
        "requester_group": {"required":True, "type": "str"},
        "retention_days": {"required":True, "type": "str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["ci"],module.params["cr"],module.params["artifacts_user"],
                            module.params["artifacts_password"],module.params["state_file_url"],
                            module.params["lookup_file"],module.params["ritm_number"],module.params["requester_name"],
                            module.params["requester_group"],module.params["retention_days"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
