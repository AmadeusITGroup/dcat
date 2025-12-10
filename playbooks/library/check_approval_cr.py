import requests
import re
import urllib.parse
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: 

description: Validating if both Server Owner and Application Removal TRs are created for the given CR.

version_added: "1.0.0"

options:
    username:
        description: username for winaproach API.
        required: true
        type: str
    
    password:
        description: password for winaproach API.
        required: true
        type: str
    
    win_target:
        description: endpoint for winaproach API. 
        required: true
        type: str   

    cr:
        description: Change Record of corresponding request.
        required: true  
        type: str               
'''

EXAMPLES = r'''
# Module usage example 
- create_ci_list_final:
            username: '{{ winaproach username }}'
            password: '{{ winaproach password }}'
            win_target: "{{winaproach_endpoint}}"
            cr: "{{change_record}}"
'''

RETURN = r'''
# Module return values
flag:
    description: Boolean flag indicating if both TRs are created.
    type: bool
    returned: always
'''

def get_data(username, password, win_target, cr):
    session = requests.Session()
    url="https://"+win_target+"/aproach-api/v1.0/changerecords/"+cr
    session.auth = (username, password)
    response = session.get(url)
    data = response.json()
    overview_texts = [entry.get("text", "") for entry in data.get("overviews", [])]

    flag = False
    flag = all(
        any(required in text for text in overview_texts)
        for required in [
            "CSTY:DECO:DCAT : DECO - Server Owner Approval",
            "CSTY:DECO:DCAT : DECO - App Owner Approval"
        ]
    )

    return flag

     
def main():
    returnvalue = {}
    fields = {
        "username":{"required":True, "type":"str", "no_log": True},
        "password":{"required":True, "type":"str", "no_log": True},
        "win_target":{"required":True, "type":"str"},
        "cr": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        flag = get_data(module.params["username"],
                            module.params["password"],module.params["win_target"],
                            module.params["cr"])
        returnvalue["flags"] = flag
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["ci_list"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
