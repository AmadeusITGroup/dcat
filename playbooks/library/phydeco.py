from ansible.module_utils.basic import *
import warnings
import requests
import time
import base64
import json
warnings.simplefilter(action='ignore', category=FutureWarning)
 
DOCUMENTATION = r'''
---
module: Backup node decommission task from ISP
 
description: Backup node decommission task from ISP
 
version_added: "1.0.0"
 
options:
    username:
        description: Username for the AWX API call.
        required: true
        type: str
    password:
        description: Password for the AWX API call.
        required: true
        type: str
    url:
        description: AWX template url
        required: true
        type: str
    ci:
        description: host list which is getting passed
        required: true
        type: list
    tr: 
       description: Task record ID for backup
       required: true
       type: str 
    retention_days: 
       description: retention_days for backup node decommission
       required: true
       type: str                     

'''
 
EXAMPLES = r'''
    - name: Implementation partial that is closing the implementation as partial
        deco_jobs:
            url: "{{AWX_URL}}"  
            username: "{{ auth_username }}"
            password: "{{ auth_password }}"
            ci: '{{ host_list.vm_list }}'
            cr: "'{{ cr }}'"
            graceperiod_flag: "'{{ graceperiod_flag }}'"
            retention_days: "'{{ retention_days }}'"
            requester_name: "{{ requester_name }}"
            requester_group: "{{ requester_group }}"
        delegate_to: localhost                
        register: job_status
'''
def job(url,username,password,ci,cr,ritm_number,graceperiod_flag,retention_days,requester_name,requester_group,pillar,mit_ticket):
    host = ""
    for x in ci:
        host += str(" - "+"hosts:"+" "+"'"+x+"'"+"\r\n")
        time.sleep(1)
    url="https://"+ url +"/api/v2/job_templates/23615/launch/"
    # headers={"Content-Type":"application/json"}
    # data = {"name": "DCAT VM PHY DECO","description": "DCAT VM PHY DECO","job_type": "run","inventory": 1457,"project": 21855,"playbook": "playbooks/launch_dev_phydeco.yml","scm_branch": "","forks": 0,"limit": "","verbosity": 0,"extra_vars": "---","job_tags": "","force_handlers": "false","skip_tags": "","start_at_task": "","timeout": 0,"use_fact_cache": "false","execution_environment": 4,"host_config_key": "","ask_scm_branch_on_launch": "false","ask_diff_mode_on_launch": "false","ask_variables_on_launch": "true","ask_limit_on_launch": "false","ask_tags_on_launch": "false","ask_skip_tags_on_launch": "false","ask_job_type_on_launch": "false","ask_verbosity_on_launch": "false","ask_inventory_on_launch": "false","ask_credential_on_launch": "false","ask_execution_environment_on_launch": "false","ask_labels_on_launch": "false","ask_forks_on_launch": "false","ask_job_slice_count_on_launch": "false","ask_timeout_on_launch": "false","ask_instance_groups_on_launch": "false","survey_enabled": "false","become_enabled": "false","diff_mode": "false","allow_simultaneous": "false","job_slice_count": 4,"webhook_service": "","webhook_credential": "null","prevent_instance_group_fallback": "false"}
    ci_data = "associated_cis:\r\n"+host+"cr: "+cr+"\r\ngraceperiod_flag: "+graceperiod_flag+"\r\nritm_number: "+ritm_number+"\r\nretention_days: "+retention_days+"\r\nrequester_name: "+requester_name+"\r\nrequester_group: "+requester_group+"\r\npillar: "+pillar+""+"\r\nmit_ticket: "+mit_ticket+""
    
    payload = json.dumps({
    "extra_vars": ci_data
    })
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()    
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_credentials}',
    }
    result = requests.request("POST", url, headers=headers, data=payload , verify=False)
    
    #result=requests.post(url,auth=(username, password),json=data,headers=headers,verify=False)
    time.sleep(20)
    status = result.json()
    return(status)

 
def main():
    returnValue = dict()
    fields = {  
        "url":{"required":True, "type":"str"},           
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True},
        "ci":{"required":True, "type":"list"},
        "cr":{"required":True, "type":"str"},
        "ritm_number":{"required":True, "type":"str"},
        "graceperiod_flag": {"required":True, "type":"str"},
        "retention_days":{"required":True, "type":"str"},
        "requester_name":{"required":True, "type":"str"},
        "requester_group":{"required":True, "type":"str"},
        "pillar":{"required":False, "type":"str"}, 
        "mit_ticket":{"required":False, "type":"str"}    
    }
    module = AnsibleModule(argument_spec = fields)  
    if module.params['pillar'] is None or module.params['pillar'] == '':
        module.params['pillar'] = 'F'
    try:
        status = job(module.params["url"],module.params["username"],module.params["password"],
                        module.params["ci"],module.params["cr"],module.params["ritm_number"],
                        module.params["graceperiod_flag"],module.params["retention_days"],
                        module.params["requester_name"],
                        module.params["requester_group"],module.params["pillar"],module.params["mit_ticket"])
        returnValue["status"] = status        
        module.exit_json(**returnValue)           
    except Exception as e:
        returnValue["status"] = "[ERROR]" + str(e)
        module.exit_json(**returnValue)
 
         
if __name__ == '__main__':
    main()
