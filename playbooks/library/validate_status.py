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
    - thineshkumar R (@thr)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_ref:
            hostname: "{{hostname}}"
          register: update_status
          delegate_to: localhost
'''


def write_data(ritm_number,artifacts_user,artifacts_password,state_file_url,lookup_file):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file
    session.auth = (artifacts_user, artifacts_password)
    response = session.get(url)
    data = response.text
    data = pd.read_csv(StringIO(data))
    filtered_data = data[data['ritm_number'] == ritm_number]
    if not filtered_data[(filtered_data['app_tr_status'] == 'open') | (filtered_data['owner_tr_status'] == 'open')].empty:
        cr_check = filtered_data['cr'].unique().tolist()
        cr = str(cr_check[0]) if cr_check else "None"        
        status = "RITM has open status"
        ci_list = filtered_data['ci'].unique().tolist()
        app_tr = filtered_data['app_tr'].unique().tolist()
        #app_tr = str(appl_tr[0]) if appl_tr else "None"
        owner_tr = filtered_data['owner_tr'].unique().tolist()
        #owner_tr = str(own_tr[0]) if own_tr else "None"
        requester_na = filtered_data['requester_name'].unique().tolist()
        requester_name = str(requester_na[0]) if requester_na else "None"
        requester_gr = filtered_data['requester_group'].unique().tolist()
        requester_group = str(requester_gr[0]) if requester_gr else "None"  
        retention_day = filtered_data['retention_days'].unique().tolist()
        retention_days = str(retention_day[0]) if retention_day else "None"         
        return cr,ci_list,ritm_number,app_tr,owner_tr,requester_name,requester_group,retention_days,status
    else:
        cr_check = filtered_data['cr'].unique().tolist()
        status = "RITM closed"
        cr = str(cr_check[0]) if cr_check else "None"
        ci_list = filtered_data['ci'].unique().tolist()
        app_tr = filtered_data['app_tr'].unique().tolist()
        #app_tr = str(appl_tr[0]) if appl_tr else "None"
        owner_tr = filtered_data['owner_tr'].unique().tolist()
        #owner_tr = str(own_tr[0]) if own_tr else "None"
        requester_na = filtered_data['requester_name'].unique().tolist()
        requester_name = str(requester_na[0]) if requester_na else "None"
        requester_gr = filtered_data['requester_group'].unique().tolist()
        requester_group = str(requester_gr[0]) if requester_gr else "None"  
        retention_day = filtered_data['retention_days'].unique().tolist()
        retention_days = str(retention_day[0]) if retention_day else "None"         
        return cr,ci_list,ritm_number,app_tr,owner_tr,requester_name,requester_group,retention_days,status    
  

def main():
    returnvalue = {}
    fields = {
        "ritm_number":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str"},
        "artifacts_password":{"required":True, "type":"str"},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["ritm_number"],module.params["artifacts_user"],
                            module.params["artifacts_password"],module.params["state_file_url"],
                            module.params["lookup_file"])
        cr=status[0]
        ci=status[1]
        ritm=status[2]
        app_tr=status[3]
        owner_tr=status[4]
        requester_name=status[5]
        requester_group=status[6]
        retention_days=status[7]
        status=status[8]
        if "open" in status:
            returnvalue["status"] = status
            returnvalue["cr"] = cr
            returnvalue["ci"] = ci
            returnvalue["ritm"] = ritm
            returnvalue["app_tr"] = app_tr
            returnvalue["owner_tr"] = owner_tr
            returnvalue["requester_name"] = requester_name
            returnvalue["requester_group"] = requester_group
            returnvalue["retention_days"] = retention_days            
            module.exit_json(**returnvalue)
        else:
            returnvalue["status"] = status
            returnvalue["cr"] = cr
            returnvalue["ci"] = ci
            returnvalue["ritm"] = ritm
            returnvalue["app_tr"] = app_tr
            returnvalue["owner_tr"] = owner_tr            
            returnvalue["requester_name"] = requester_name
            returnvalue["requester_group"] = requester_group
            returnvalue["retention_days"] = retention_days              
            module.exit_json(**returnvalue)   
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
