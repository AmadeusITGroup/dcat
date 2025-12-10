import time
import warnings
from ansible.module_utils.basic import AnsibleModule
import requests
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

def write_data(username,password,url,group):
    session = requests.Session()
    url="https://"+url+"/api/v2/json/groups/?max=2977"
    session.auth = (username, password)
    response = session.get(url)
    data = response.json()
    #group="CFS-PEA-IPD-VIF"
    df=[]
    for val in data['groups']:
      if group in val['chorus_codeid']['description']:
        group_code = val['code']
        break
        # df.append(val['description'])
        # group_code = df[0].split('Abbreviation:')[1].split('\n')[0].replace('\r','').strip()
    return group_code
 
def main():
    returnvalue = {}
    fields = {
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "url":{"required":True, "type":"str"},
        "group": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["username"],
                            module.params["password"],module.params["url"],
                            module.params["group"])
        returnvalue["status"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Exception]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
