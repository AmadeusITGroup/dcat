import requests
import json
import base64
import warnings
from ansible.module_utils.basic import AnsibleModule
warnings.simplefilter(action='ignore', category=FutureWarning)

def file_content(filepath,template_id,awx,user_name,pass_word):
    with open(filepath) as f:
      json_data = json.load(f)
    url = "https://"+awx+"/api/v2/workflow_job_templates/"+template_id+"/launch/"
    payload = json.dumps({
    "extra_vars": json_data
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
        "filepath":{"required":True, "type":"str"},
        "template_id":{"required":True, "type":"str"},
        "awx":{"required":True, "type":"str"},
        "user_name":{"required":True, "type":"str"},
        "pass_word":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = file_content(module.params["filepath"],
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