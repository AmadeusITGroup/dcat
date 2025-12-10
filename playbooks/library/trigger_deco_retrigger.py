import requests
import json
import base64
import time
import warnings
from ansible.module_utils.basic import AnsibleModule
warnings.simplefilter(action='ignore', category=FutureWarning)


def file_content(cr,ci,graceperiod_flag,requester_name,requester_group,retention_days,ritm_number,pillar,template_id,awx,user_name,pass_word):    
    host = ""
    for x in ci:
        host += str(" - "+"hosts:"+" "+"'"+x+"'"+"\r\n")
        time.sleep(1)    
    ci_data = "associated_cis:\r\n"+host+"cr: "+cr+"\r\ngraceperiod_flag: '"+graceperiod_flag+"'\r\nretention_days: "+retention_days+"\r\nrequester_name: "+requester_name+"\r\nrequester_group: "+requester_group+"\r\nritm_number: "+ritm_number+"\r\npillar: "+pillar+""
    url = "https://"+awx+"/api/v2/job_templates/"+template_id+"/launch/"
    payload = json.dumps({
    "extra_vars": ci_data
    })
    username = user_name
    password = pass_word    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()    
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_credentials}',
    }

    response = requests.request("POST", url, headers=headers, data=payload , verify=False)
    return response.text


def main():
    returnvalue = {}
    fields = {
        "cr":{"required":True, "type":"str"},
        "ci":{"required":True, "type":"list"},
        "graceperiod_flag":{"required":True, "type":"str"},
        "requester_name":{"required":True, "type":"str"},
        "requester_group":{"required":True, "type":"str"},
        "retention_days":{"required":True, "type":"str"},
        "ritm_number":{"required":True, "type":"str"},
        "pillar":{"required":True, "type":"str"},
        "template_id":{"required":True, "type":"str"},
        "awx":{"required":True, "type":"str"},
        "user_name":{"required":True, "type":"str"},
        "pass_word":{"required":True, "type":"str"}        
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = file_content(module.params["cr"],
                            module.params["ci"],
                            module.params["graceperiod_flag"],
                            module.params["requester_name"],
                            module.params['requester_group'],
                            module.params['retention_days'],
                            module.params['ritm_number'],
                            module.params['pillar'],
                            module.params["template_id"],
                            module.params["awx"],
                            module.params["user_name"],
                            module.params["pass_word"])
        returnvalue["status"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()