import urllib
import requests
from ansible.module_utils.basic import AnsibleModule
# pylint: disable=E1101
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
DOCUMENTATION = r'''
---
module: 

description: Fethcing the VM status is "Deco In Progress".

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
            instance_id: '{{ instanceid }}'
'''

RETURN = r'''
# Module return values
server_name:
    description: Name of VM passed into module.
    type: str
    returned: always
    sample: 'vmdecowprj02'
changed:
    description: Boolean indicating if the module made changes to the target or delegated host.
    type: bool
    returned: always
    sample: false

cmdb_result:
    description: The  message fetched from the module.
    type: str
    returned: always
    sample: "{{CMDB_URL}}"

'''

def cmdb_fetch(conn_str,server_name,cmdb_server,user_name,pass_word,instance_id):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    # TODO: Remove the urls:
    # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
    # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    try :
        # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # body = {'username': user_name, 'password': pass_word}
        # response = requests.post(url=login_url, data=body, headers=headers)
        # result = str(response.status_code) + ' ' + response.reason
        # auth_token = response.text
        # Login
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=pass_word)
        if "NO LOGIN" in JWT_AUTH_TOKEN: #response.status_code != requests.codes.ok:
            final_msg = 'could not get server CI: '+ JWT_AUTH_TOKEN
            JWT_AUTH_TOKEN = None
            return final_msg

        else:
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
            result = str(response.status_code) + ' ' + response.reason
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                         cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None

            if response.status_code != requests.codes.ok:
                final_msg = 'could not get server CI: '+result
                raise Exception(final_msg)

            else:
                result = response.json()
                entries = result['entries']
                
                if len(entries) == 1:
                    entry = entries[0]
                    values = entry['values']
                    status_of_server = values['StatusReason']
                    if status_of_server == "Deco in Progress": #
                        final_msg ="You are good to proceed with deco for server " + server_name + "."
                    else:
                        final_msg = "The server "+server_name+" is not Deco In Progress status."+" Kindly check with application team"

                elif len(entries)== 0:
                    final_msg = "Unable to fetch cmdb status of server as no entries exist for the server"

                else:
                    if instance_id =="":
                        final_msg = "Unable to fetch cmdb status of server as duplicate entries exist and no instance ID provided"
                    else:
                        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                                   cmdb_server=cmdb_server,
                                                                   password=pass_word)
                        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != 200:
                            final_msg_cmdb = 'An error occurred, Login failed with error: ' + str(JWT_AUTH_TOKEN)
                            JWT_AUTH_TOKEN = None
                            return final_msg_cmdb
                        headers = {
                            'Content-Type': 'application/json',
                            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
                        }
                        query=qprefix+' and  Name="'+server_name+'"'+' and  InstanceId="'+instance_id+'"'
                        encoded_query = urllib.parse.quote(query)
                        fields = 'Name,RequestId,AssetID,InstanceId,' + fieldname_1  +' , ' + fieldname_2
                        parameters = 'q=' + encoded_query + '&fields=values(' + fields + ')'
                        url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
                        response = requests.get(url=url, headers=headers)
                        if JWT_AUTH_TOKEN is not None:
                            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                            JWT_AUTH_TOKEN = None
                        result = str(response.status_code) + ' ' + response.text

                        if response.status_code != requests.codes.ok:
                            final_msg = 'could not get server CI: '+result
                            raise Exception(final_msg)

                        else:
                            result = response.json()
                            entries = result['entries']    

                            if len(entries)== 1:
                                entry = entries[0]
                                values = entry['values']
                                status_of_server = values['StatusReason']
                                if status_of_server == "Deco in Progress": 
                                    final_msg ="You are good to proceed with deco for server  " + server_name + "."
                                else:
                                    final_msg = "The server "+server_name+" is not Deco In Progress."+" Kindly check with application team"
                            elif len(entries)== 0:
                                final_msg = "Unable to fetch cmdb status of server as duplicate entries exist but instance id doesnt match"
                            else:
                                final_msg = "Unable to fetch cmdb status of server as duplicate entries exist with same instance id"
        # response = requests.post(url=logout_url, headers=headers)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
            result = str(response.status_code) + ' ' + response.reason
        return final_msg

    except Exception as err: # pylint: disable=broad-except
        final_msg = "Exception in CMDB FETCH module.Kindly check if inputs are valid :"+str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        return final_msg

# print(cmdb_fetch(server_name,cmdb_server,user_name,pass_word,instance_id))
def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":True, "type":"str"},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str"},
         "pass_word":{"required":True, "type":"str"},
         "instance_id":{"required":True, "type":"str"}

    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:

        cmdb_result = cmdb_fetch(conn_str=module.params["conn_str"],
                                 server_name = module.params["server_name"],
                                  cmdb_server= module.params["cmdb_server"],
                                  user_name= module.params["user_name"],
                                  pass_word= module.params["pass_word"],
                                  instance_id=module.params["instance_id"] )
        returnvalue["cmdb_result"] = cmdb_result
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                        cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except

        returnvalue["cmdb_result"]="Exception occurred while fetching CMDB.Kindly check. " +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                        cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
