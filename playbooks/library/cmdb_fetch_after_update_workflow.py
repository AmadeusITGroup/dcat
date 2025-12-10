import urllib
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
# pylint: disable=E1101
DOCUMENTATION = r'''
---
module: 

description: Fetching the CMDB Status.

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

    instance_id:
        description: instance_id for the Server.
        required: true
        type: str         
    
'''

EXAMPLES = r'''
# Module usage example 
- Update_CMDB:
            server_name: '{{ inventory_hostname }}'
            cmdb_server: "{{cmdb_url}}"
            user_name: "{{creds.username}}"
            PASSWORD: "{{creds.password}}"
            instance_id: '{{ instanceid }}'
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

CMDB_RESULT:
    description: The Update message fetched from the module.
    type: str
    returned: always

'''


def cmdb_after_update(conn_str,server_name,cmdb_server,user_name,pass_word,instance_id):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    # TODO: Remove Login details:
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # body = {'username': user_name, 'password': pass_word}
    # response = requests.post(url=login_url, data=body, headers=headers)
    # result = str(response.status_code) + ' ' + response.reason
    # auth_token = response.text
    
    try:
        # Login
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=pass_word)
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
            final_msg_cmdb = 'An error occurred: ' + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            return final_msg_cmdb
    
        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
            }
        query = qprefix + ' and  Name="' + server_name + '"'
        encoded_query = urllib.parse.quote(query)
        fields = 'Name,RequestId,AssetID,' + fieldname_1  +' , ' + fieldname_2
        parameters = 'q=' + encoded_query  + '&fields=values(' + fields + ')'
        url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
        response = requests.get(url=url, headers=headers)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        result = str(response.status_code) + ' ' + response.reason
        if response.status_code != requests.codes.ok:
            final_msg_cmdb = 'could not get server CI: '+result
            raise Exception(final_msg_cmdb)
    
        result = response.json()
        entries = response.json()['entries']
        #print(response.json())
        if len(entries) == 1:
            entry = entries[0]
            values = entry['values']
            new_content_1 = values[fieldname_1]
            new_content_2 = values[fieldname_2]
            if new_content_1 =="Deployed" and new_content_2 =="Deco in Progress":
                final_msg_cmdb = "CMDB STATUS UPDATED SUCCESSFULLY that is status field to (Deployed),status reason field to (Deco in Progress)."
            else:
                final_msg_cmdb = "Failed to update CMDB status kindly check for connection issue"
    
        elif len(entries)== 0:
            final_msg_cmdb = "no entries exist for the server"
        else:
            JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                       cmdb_server=cmdb_server,
                                                       password=pass_word)
            if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
                final_msg_cmdb = 'An error occurred: ' + str(JWT_AUTH_TOKEN)
                JWT_AUTH_TOKEN = None
                return final_msg_cmdb
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
            }
            query = qprefix + ' and  Name="' + server_name + '"' + ' and  InstanceId="' + instance_id + '"'
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
                final_msg_cmdb = 'could not get server CI when trying to check if cmdb is updated : '+result
                raise Exception(final_msg_cmdb)
    
            result = response.json()
            entries = response.json()['entries']
            if len(entries) == 1:
                entry = entries[0]
                values = entry['values']
                new_content_1 = values[fieldname_1]
                new_content_2 = values[fieldname_2]
                if new_content_1 == "Deployed" and new_content_2 == "Deco in Progress":
                    final_msg_cmdb = "CMDB STATUS UPDATED SUCCESSFULLY that is status field to (Deployed) ,status reason field to (Deco in Progress)."
                else:
                    final_msg_cmdb = "Failed to update CMDB kindly check module or connection issue"
            elif len(entries)== 0:
                final_msg_cmdb = "no entries exist for the server"
    
            else:
                final_msg_cmdb = "Failed to update CMDB status kindly check either duplicate entries exists or error fetching the data with given inputs after updating in cmdb"

    except Exception as err: # pylint: disable=broad-except
        final_msg_cmdb = "Exception in cmdb update module.Kindly check if inputs are valid :"+str(err)+", Error code: " + str(response.status_code)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
    return final_msg_cmdb

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
        cmdb_result_after = cmdb_after_update(conn_str=module.params["conn_str"],
                                              server_name = module.params["server_name"],
                                              cmdb_server= module.params["cmdb_server"],
                                              user_name= module.params["user_name"],
                                              pass_word= module.params["pass_word"],
                                              instance_id= module.params["instance_id"])
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        if cmdb_result_after== "CMDB STATUS UPDATED SUCCESSFULLY":
            returnvalue["cmdb_result_after"] = cmdb_result_after
            returnvalue['changed'] = True
            # module.exit_json(**returnvalue)
        else:
            returnvalue["cmdb_result_after"] = cmdb_result_after
            # module.exit_json(**returnvalue)
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["cmdb_result_after"] = "Exception occurred while Updating CMDB.Kindly check. " + str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
