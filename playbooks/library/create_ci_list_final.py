import requests
import re
import urllib.parse
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: 

description: Fetching the CI string from CR Overview of the corresponding request to get complete list of CIs

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
            win_target: "{{winaproach endpoint}}"
            cr: "{{change record}}"
'''

RETURN = r'''
# Module return values
ci_list:
    description: list containing all CI names which are part of the request.
    type: list
    returned: always

'''

def get_data(username, password, win_target, cr):
    ci_list = []
    session = requests.Session()
    url="https://"+win_target+"/aproach-api/v1.0/changerecords/"+cr
    session.auth = (username, password)
    response = session.get(url)
    data = response.json()
    output = data['overviews']
    ci_string = output[0].get('text', '')
    match = re.search(r'\[([^\[\]]+)\]', ci_string)
    if match:
        ci_list = [ci.strip() for ci in match.group(1).split(',')]
    else:
        raise ValueError("No CI list found in the response text.")
    
    return ci_list

     
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
        ci_list = get_data(module.params["username"],
                            module.params["password"],module.params["win_target"],
                            module.params["cr"])
        returnvalue["ci_list"] = ci_list
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["ci_list"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
