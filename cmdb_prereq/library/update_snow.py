from ansible.module_utils.basic import *
import warnings
import requests
import json
warnings.simplefilter(action='ignore', category=FutureWarning)

def update_snow(action,ritm_number,status,comments,username,password):
    try:
        url = "<service_now_url>?task="+ritm_number+"&action="+action
        payload = json.dumps({
            "status": status,
            "comments": comments
        })
        headers = {
            'Content-Type': 'Application/json',
            'Accept': 'Application/json',
        }
        response=requests.patch(url,auth=(username, password),data=payload,headers=headers)
        result = response.json()
        return result
    except Exception as e:
        result = "ERROR :"+ str(e)+", Error code: " + str(response.status_code)
        return result    

def main():
    returnValue = dict()
    fields = {  
        "action":{"required":True, "type":"str"},           
        "ritm_number":{"required":True, "type":"str"},
        "status":{"required":True, "type":"str"},
        "comments":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "password": {"required":True, "type":"str"}      
    }
    module = AnsibleModule(argument_spec = fields)  
    try:
        api_out = update_snow(module.params["action"],module.params["ritm_number"],
                     module.params["status"],module.params["comments"],
                     module.params["username"],module.params["password"]
                     )
        returnValue["api_call"] = api_out        
        module.exit_json(**returnValue)           
        
    except Exception as e:
        returnValue["api_call"] = "[ERROR]" + str(e)
        module.exit_json(**returnValue)

         
if __name__ == '__main__':
    main()