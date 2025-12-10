import urllib
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
# pylint: disable=E1101
DOCUMENTATION = r'''
---
module: 

description: Fethcing the server status is "Deco In Progress".

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

    instance_id:
        description: instance_id for the Server.
        required: true
        type: str                
    
author:
    - Leethu T.L (@pltl)
'''

EXAMPLES = r'''
# Module usage example 
- server_details:
            server_name: '{{ inventory_hostname }}'
            cmdb_server: "{{CMDB_URL}}"
            user_name: "{{creds.username}}"
            pass_word: "{{creds.password}}"
'''

RETURN = r'''
# Module return values
server_name:
    description: Name of Server passed into module.
    type: str
    returned: always
    sample: 'vmdecowprj02'
changed:
    description: Boolean indicating if the module made changes to the target or delegated host.
    type: bool
    returned: always
    sample: false

cmdb_result_fqdn:
    description: The  message fetched from the module.
    type: str
    returned: always
    sample: "{{CMDB_URL}}" 

'''

def cmdb_fetch_fqdn(conn_str,server_name,cmdb_server,user_name,pass_word):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    # TODO: Remove the urls:
    # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
    # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'Domain'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    s_name = server_name.lower()
    try :
        # TODO: Remove Login details:
        # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # body = {'username': user_name, 'password': pass_word}
        # response = requests.post(url=login_url, data=body, headers=headers)
        # result = str(response.status_code) + ' ' + response.reason
        # auth_token = response.text
        
        # Login
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=pass_word)
        
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
            final_msg_cmdb = "Unable to get server CI: " + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            return final_msg_cmdb

        else:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
            }
            query = qprefix + ' and  Name="' + s_name + '"'
            encoded_query = urllib.parse.quote(query)
            fields = 'Name,RequestId,AssetID,InstanceId,' + fieldname_1
            parameters = 'q=' + encoded_query + '&fields=values(' + fields + ')'
            url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
            response = requests.get(url=url, headers=headers)
            # Logout
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                              cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None
            result = str(response.status_code) + ' ' + response.reason

            if response.status_code != requests.codes.ok:
                final_msg = 'Unable to get server CI: '+result
                raise Exception(final_msg)

            else:
                result = response.json()
                entries = response.json()['entries']
                if len(entries) == 1:
    ############# checking the status reason part ###################
                    entry = entries[0]
                    values = entry['values']
                    status_of_server = values['Domain']
                    if status_of_server != "":
                        final_msg = status_of_server
                    else:
                        final_msg = "Unable to fetch fqdn as domain field is blank "

                elif len(entries)== 0:
                    final_msg = "Unable to fetch fqdn of server as no entries exist for the server"

                else:
                    final_msg = "Unable to fetch fqdn of server as duplicate entries exist"

        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        
        return final_msg

    except Exception as err: # pylint: disable=broad-except
        final_msg = "Exception in fqdn fetch module.Kindly check if inputs are valid :"+str(err)+", Error code: " + str(response.status_code)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        return final_msg

# print(cmdb_fetch_fqdn(server_name,cmdb_server,user_name,pass_word))
def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":False, "type":"str"},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str","no_log":True},
         "pass_word":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:

        cmdb_result_fqdn = cmdb_fetch_fqdn(conn_str=module.params["conn_str"],
                                           server_name = module.params["server_name"],
                                          cmdb_server= module.params["cmdb_server"],
                                          user_name= module.params["user_name"],
                                          pass_word= module.params["pass_word"])
        returnvalue["cmdb_result_fqdn"] = cmdb_result_fqdn
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except

        returnvalue["cmdb_result_fqdn"]="Exception occurred while fetching CMDB.Kindly check. " +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()