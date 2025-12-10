import urllib
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
# pylint: disable=E1101
DOCUMENTATION = r'''
---
module: 

description: Updating the CMDB Status to'' and status reason to ''.

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
        
    status_value:
        description: Status value of the field Status which needs to be updated in the CMDB.
        required: true
        type: str
    
    status_reason_value:
        description: Status Reason Value of the field Status Reason which needs to be updated in CMDB
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
- Update_CMDB:
            server_name: '{{ inventory_hostname }}'
            cmdb_server: "{{CMDB_URL}}"
            status_value: 'End of Life' #'End of Life'#'Deployed'
            status_reason_value: 'Obsolete'  #'Obsolete' #'Not in Production'
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
    description: The Update message fetched from the module.
    type: str
    returned: always
    sample: "{{CMDB_URL}}"

'''

def cmdb_update(conn_str,server_name,cmdb_server,user_name,pass_word,status_value,status_reason_value,instance_id):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    # TODO: Remove the urls:
    # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
    # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    fieldname_3 = 'zPrevAssetID' ####This field is for syncing the cmdb with application
    fieldname_4 = 'AdminIP'
    new_content_3 ='CORE'
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
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
        # Logout
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        result = str(response.status_code) + ' ' + response.reason

        if response.status_code != requests.codes.ok:
            raise ValueError('could not get server CI: '+result)
            # final_msg = '[Exception] could not get server CI: '+result

        result = response.json()
        entries = response.json()['entries']
        #print(entries)
        if len(entries) == 1:
            ############# Updating the cmdb value ###################
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
            entry = entries[0]
            values = entry['values']
            request_id = values['RequestId']
            url = entry_url + '/BMC.CORE:BMC_ComputerSystem/' + request_id
            admin_ip = ''
            body = {'values': {fieldname_1: status_value, fieldname_2: status_reason_value,fieldname_3: new_content_3,fieldname_4: admin_ip }}
            response = requests.put(url=url, json=body, headers=headers)
            # logout
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                         cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None
            result = str(response.status_code) + ' ' + response.reason

            if response.status_code != requests.codes.no_content:
                #print('Error, response.text = '+repr(response.text))
                final_msg ="Exception while updating the CMDB status. "+result
            else:
                final_msg = "CMDB STATUS UPDATED SUCCESSFULLY that is status field to ("+status_value+") , status reason field to ("+status_reason_value+") and set ADMIN IP to null."

        elif len(entries)== 0:
            final_msg = "Exception no entries exist for the server"

        else:
            if instance_id =="":
                final_msg = "Exception Duplicate entries exist and no instance ID provided"
            else:
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
                query=qprefix+' and  Name="'+server_name+'"'+' and  InstanceId="'+instance_id+'"'
                encoded_query = urllib.parse.quote(query)
                fields = 'Name,RequestId,AssetID,InstanceId,' + fieldname_1  +' , ' + fieldname_2
                parameters = 'q=' + encoded_query + '&fields=values(' + fields + ')'
                url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
                response = requests.get(url=url, headers=headers)
                # Logout
                if JWT_AUTH_TOKEN is not None:
                    logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                             cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                    JWT_AUTH_TOKEN = None
                result = str(response.status_code) + ' ' + response.text

                if response.status_code != requests.codes.ok:
                    raise ValueError('could not get server CI: '+result)
                    # final_msg = 'Exception could not get server CI: '+result

                result = response.json()
                entries = response.json()['entries']               
                if len(entries)== 1:
                    JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                               cmdb_server=cmdb_server,
                                                               password=pass_word)
                    if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
                        final_msg_cmdb = "An error occurred while Logging in: " + str(JWT_AUTH_TOKEN)
                        JWT_AUTH_TOKEN = None
                        return final_msg_cmdb
                    entry = entries[0]
                    values = entry['values']
                    request_id = values['RequestId']
                    url = entry_url + '/BMC.CORE:BMC_ComputerSystem/' + request_id
                    admin_ip = ''
                    body = {'values': {fieldname_1: status_value, fieldname_2: status_reason_value,fieldname_3: new_content_3,fieldname_4: admin_ip }}
                    response = requests.put(url=url, json=body, headers=headers)
                    # logout
                    if JWT_AUTH_TOKEN is not None:
                        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                                 cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                        JWT_AUTH_TOKEN = None
                    result = str(response.status_code) + ' ' + response.reason
                    if response.status_code != requests.codes.no_content:
                        #print('Error, response.text = '+repr(response.text))
                        final_msg ="Exception while updating the CMDB status. "+result
                        raise Exception(final_msg)
                    else:
                        final_msg = "CMDB STATUS UPDATED SUCCESSFULLY that is status field to ("+status_value+") , status reason field to ("+status_reason_value+") and set ADMIN IP to null."
                elif len(entries)== 0:
                    final_msg = "Exception Duplicate entries exist but instance id doesnt match"
                else:
                    final_msg = "Exception Duplicate entries exist with same instance id"
        # Logout
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
            result = str(response.status_code) + ' ' + response.reason
        # response = requests.post(url=logout_url, headers=headers)
        return final_msg

    except Exception as err: # pylint: disable=broad-except
        final_msg = "Exception in CMDB UPDATE MODULE.Kindly check if inputs are valid :"+str(err) # +", Error code: " + str(response.status_code)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        return final_msg

def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":True, "type":"str"},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str"},
         "pass_word":{"required":True, "type":"str"},
         "status_value":{"required":True, "type":"str"},
         "status_reason_value":{"required":True, "type":"str"},
         "instance_id":{"required":True, "type":"str"}

    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:

        cmdb_result = cmdb_update(conn_str=module.params["conn_str"],
                                  server_name = module.params["server_name"],
                                  cmdb_server= module.params["cmdb_server"],
                                  user_name= module.params["user_name"],
                                  pass_word= module.params["pass_word"],
                                  status_value=module.params["status_value"],
                                  status_reason_value=module.params["status_reason_value"],
                                  instance_id=module.params["instance_id"] )
        if cmdb_result == "CMDB STATUS UPDATED SUCCESSFULLY":
            returnvalue["cmdb_result"] = cmdb_result
            returnvalue['changed'] = True
            # module.exit_json(**returnvalue)
        else:
            returnvalue["cmdb_result"] = cmdb_result
            # module.exit_json(**returnvalue)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["cmdb_result"]="Exception occurred while Updating CMDB.Kindly check. " +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()