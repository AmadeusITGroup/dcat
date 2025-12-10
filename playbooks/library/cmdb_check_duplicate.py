import urllib
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
# pylint: disable=E1101
DOCUMENTATION = r'''
---
module: 

description: Checking if duplicate entries of server exists in bmc remedy ''.

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
        description: Username for the CMDB login.
        required: true
        type: str
        
    Password:
        description: Password for the CMDB login.
        required: true
        type: str               
    
'''

EXAMPLES = r'''
# Module usage example 
- cmdb_check_duplicate:
            server_name: '{{ inventory_hostname }}'
            cmdb_server: "{{cmdb_url}}"
            user_name: "{{creds.username}}"
            pass_word: "{{creds.password}}"

'''

RETURN = r'''
# Module return values
server_name:
    description: Name of VM passed into module.
    type: str
    returned: always
changed:
    description: Boolean indicating if the module made changes to the target or delegated host.
    type: bool
    returned: always

cmdb_result:
    description: The check fro duplicate message fetched from the module.
    type: str
    returned: always
'''

def cmdb_check(conn_str,server_name,cmdb_server,user_name,pass_word):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus' 
    fieldname_2 ='StatusReason'
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    try :
        
        # Login
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=pass_word)
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
            final_msg_cmdb = "An error occurred while Logging in: " + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            return final_msg_cmdb

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
        query = qprefix + ' and  Name="' + server_name + '"'
        encoded_query = urllib.parse.quote(query)
        fields = 'Name,RequestId,AssetID,InstanceId,' + fieldname_1  +' , ' + fieldname_2
        parameters = 'q=' + encoded_query + '&fields=values(' + fields + ')'
        url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
        response = requests.get(url=url, headers=headers)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        result = str(response.status_code) + ' ' + response.reason

        if response.status_code != requests.codes.ok:
            raise ValueError('could not get server CI: '+result)
            # final_msg = 'could not get server CI: '+result

        else:
            result = response.json()
            entries = response.json()['entries']
            #print(entries)
            if len(entries) == 1:
                final_msg ="successfully fetched single entry"
            elif len(entries) == 0:             
                final_msg ="no entries exists"
            else:
                final_msg ="duplicate entries exists"

        # response = requests.post(url=logout_url, headers=headers)
        result = str(response.status_code) + ' ' + response.reason
        return final_msg

    except Exception as err: # pylint: disable=broad-except
        final_msg = "Exception in cmdb duplicate check module.Kindly check if inputs or credentials are valid :"+str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        return final_msg


# cmdb_check(server_name,cmdb_server,user_name,pass_word)

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

        cmdb_result_check = cmdb_check(conn_str=module.params["conn_str"],
                                       server_name = module.params["server_name"],
                                       cmdb_server= module.params["cmdb_server"],
                                       user_name= module.params["user_name"],
                                       pass_word= module.params["pass_word"]
 )
        returnvalue["cmdb_check_result"] = cmdb_result_check
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["cmdb_check_result"]="Exception occurred while checking the duplicate entries.Kindly check. " +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
