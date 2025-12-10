import urllib.parse
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None

DOCUMENTATION = r'''
---
module: 
description: Fetching the location information for DCM in CMDB.
version_added: "1.0.0"
options:
    server_name:
        description: Name of Server which is deleted or shutdown.
        required: true
        type: str
    cmdb_server:
        description: Server part of the API URL.
        required: true
        type: str          
    user_name:
        description: username for the CMDB login.
        required: true
        type: str 
    Password:
        description: Password for the CMDB login.
        required: true
        type: str       

'''

def get_location_dcm(conn_str,server_name,cmdb_server,user_name,pass_word):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    
    entry_url = cmdb_server + "/api/arsys/v1/entry"
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    
    try:
        # Login
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=pass_word)
        # response = requests.post(url=login_url, data=body, headers=headers)
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != 200:
            final_msg_cmdb = 'An error occurred, Login failed with error: ' + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            return final_msg_cmdb
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
        res = None
        query = qprefix + ' and  Name="' + server_name + '"'
        encoded_query = urllib.parse.quote(query)
        parameters = 'q=' + encoded_query
        url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
        response = requests.get(url=url, headers=headers)
        if JWT_AUTH_TOKEN is not None:
            # Logout
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        if response.status_code != 200:
            raise Exception("Failed to fetch data for server: " + server_name)
        entries = response.json()['entries']

        result_dict = {}
        for entry in entries:
            Ci_id = entry.get('values', {}).get('AssetID')
            SerialNum = entry.get('values', {}).get('SerialNumber')
            ProductName = entry.get('values', {}).get('Model')
            site = entry.get('values', {}).get('SiteGroup')
            building = entry.get('values', {}).get('Site')
            room = entry.get('values', {}).get('Floor')
            coordinate = entry.get('values', {}).get('Room')
            bay_rack = entry.get('values', {}).get('BayNumber_RackUnit')
        result_dict[server_name] = {"CI ID+": Ci_id, "SerialNumber":SerialNum,"ProductName+":ProductName,"Site":site,"building": building,"room": room,"coordinate": coordinate,"bay_rack": bay_rack}
    except Exception as e:
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        print("Error occurred:", e)
        return None
    finally:
        # Logout
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        # requests.post(url=logout_url, headers=headers)
    return result_dict

def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":True, "type":"str"},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str","no_log":True},
         "pass_word":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        loc_dcm = get_location_dcm(conn_str=module.params["conn_str"],
                                   server_name = module.params["server_name"],
                                   cmdb_server= module.params["cmdb_server"],
                                   user_name= module.params["user_name"],pass_word= module.params["pass_word"])
        returnvalue["status"] = loc_dcm
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
