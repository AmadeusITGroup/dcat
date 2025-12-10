import time
import warnings
import requests
warnings.simplefilter(action='ignore', category=FutureWarning)
from ansible.module_utils.basic import AnsibleModule



DOCUMENTATION = r'''
---
module: Create TR for modules using pre-approved BIRD template

description: Create TR for modules using pre-approved BIRD template

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
    bird_url:
        description: BIRD end point for TR creation and bearer token generation
        required: true
        type: str
    template_name:
        description: BIRD Template name for TR creation
        required: true
        type: str
    cr_id:
        description: Change Request No for the DECO process
        required: true
        type: str
    ci: 
       description: Collection of CI details
       required: true
       type: list
    winaproach_category:
        description: Categorizing the TR
        required: true
        type: str       
       
    
author:
    - Prashanth k (@pk)
    - Leethu TL (@ltl)
    - Thineshkumar r @thr)
'''

EXAMPLES = r'''
- name: Create TR using pre-approved template
          create_tr_bird:
            username: "{{username}}"
            password: "{{password}}"
            bird: "{{ bird_url }}"
            template_name: "{{ template_name }}"
            cr_id: "{{ cr_id }}"
            ticket_title:"{{ ticket_title }}"
            ci: "{{ inventory_hostname }}" # List of CI details
            winaproach_category: "{{ winaproach_category }}"
          register: ticket_id
          delegate_to: localhost
'''
def create_tr(username,password,bird,template_name,cr_id,ticket_title,ci,winaproach_category):
    hosts = ','.join(map(str, ci))
    session = requests.Session()
    session.verify = False
    token_url="https://"+ bird +"/auth/login-credentials"
    data={"login": username, "password": password}
    response = session.post(token_url,headers={"Content-Type":"application/json"},json=data)
    auth_token= response.json()['access_token']
    if auth_token:
        create_tr_url = "https://"+ bird +"/records/create-pre-approved-tr"
        headers={"Content-Type":"application/json",
                 "Authorization": "Bearer " + auth_token,
                 "jwt": "eyJhbGciOiJSUzUxMiJ9.eyJzdWIiOiIxMTI2ODZ-Nzg0ODEiLCJpc3MiOiJVSU0iLCJpYXQiOjE2NzcwNDgwNDF9.kVs_9ljijZDKRJLAOnYJJ6o4kYj3MZ5_38oiLQB37nsIKUTJk0weRqtYBmAE79r0lsetHbmDRZjf_vob7Y6quduUsD3bcGpNDfrgjtQ55ZcPRMMrgTcHVgbIpGm_gJ1M5GlHXd9pvGtnEVSVoGsfOsz9nnCNfwGfCFwhJjZjDsg"}
        data1={"contextName": "ics-ccb","ticketId": template_name,
               "version":"v2","importToChangeReviewBoard": False,
               "questionnaire": [{"name": "TaskParentID","value": [cr_id]},
                                 {"name": "SystemCategory", "value": [winaproach_category]},
                                 {"name": "Title", "value": [ticket_title]},
                                 {"name": "confItemName", "value":[hosts]}]}
        result=requests.post(create_tr_url,json=data1,headers=headers,verify=False)
        time.sleep(10)
        if result.status_code == '200':
            ticket_id = result.json()['ticketId']
        else:
            ticket_id = result.json()
        status = ticket_id
    else:
        status = "Unable to generate token"
    return status



def main():
    returnvalue = {}
    fields = {
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "bird":{"required":True, "type":"str"},
        "template_name":{"required":True, "type":"str"},
        "cr_id":{"required":True, "type":"str"},
        "ticket_title":{"required":True, "type":"str"},
        "ci":{"required":True, "type":"list"},
        "winaproach_category":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = create_tr(module.params["username"],
                           module.params["password"],
                           module.params["bird"],
                           module.params["template_name"],
                           module.params["cr_id"],
                           module.params["ticket_title"],
                           module.params["ci"],
                           module.params["winaproach_category"])
        returnvalue["id"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Error"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)


if __name__ == '__main__':
    main()