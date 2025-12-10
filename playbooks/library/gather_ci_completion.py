import configparser,requests,urllib
from requests.auth import HTTPBasicAuth
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None

def cmdb_fetch(conn_str,ci_list,cmdb_server,user_name,pass_word):

    server_deco = True
    idempotent_obj = []
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    # TODO: Remove the urls:
    # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
    # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
    entry_url = cmdb_server + "/api/arsys/v1/entry"

    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    for ci in ci_list:
        server_name = ci
        instance_id= ci_list[ci]
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
            if "NO LOGIN" in JWT_AUTH_TOKEN: #response.status_code != requests.codes.ok:
                server_deco = False
                final_msg = 'could not get server CI: '+JWT_AUTH_TOKEN
                JWT_AUTH_TOKEN = None
                raise ValueError(final_msg)

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
                # Logout
                if JWT_AUTH_TOKEN is not None:
                    logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                  cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                    JWT_AUTH_TOKEN = None
                result = str(response.status_code) + ' ' + response.reason

                if response.status_code != requests.codes.ok:
                    server_deco =False
                    final_msg = 'could not get server CI: '+result
                    idempotent_obj.append("FAILRE"+final_msg)

                else:
                    result = response.json()
                    entries = response.json()['entries']
                    if len(entries) == 1:
        ############# checking the status reason part ###################
                        entry = entries[0]
                        values = entry['values']
                        status_of_server = values[fieldname_1]
                        status_reson_of_server = values[fieldname_2]
                        
                        if status_of_server == "End of Life" and status_reson_of_server == "Obsolete":
                            final_msg ="You are good to proceed with Reclaiming the server " + server_name + "."
                            idempotent_obj.append("SUCCESS"+final_msg)
                        else:
                            server_deco =False
                            final_msg = "The server "+server_name+" is Not in Deco in Progress status to reclaim it."+" Kindly check with application team"
                            idempotent_obj.append("FAILRE"+final_msg)

                    elif len(entries)== 0:
                        server_deco =False
                        final_msg = "Unable to fetch cmdb status of server as no entries exist for the server"
                        idempotent_obj.append("FAILRE"+final_msg)

                    else:
                        if instance_id =="":
                            server_deco =False
                            final_msg = "Unable to fetch cmdb status of server as duplicate entries exist and no instance ID provided"
                            idempotent_obj.append("FAILRE"+final_msg)
                        else:
                            JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                                       cmdb_server=cmdb_server,
                                                                       password=pass_word)
                            if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
                                server_deco = False
                                final_msg = 'could not get server CI: ' + JWT_AUTH_TOKEN
                                JWT_AUTH_TOKEN = None
                                raise ValueError(final_msg)
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
                                server_deco =False
                                final_msg = 'could not get server CI: '+result
                                idempotent_obj.append("FAILRE"+final_msg)

                            else:
                                result = response.json()
                                entries = response.json()['entries']               
                                if len(entries)== 1:
                                    entry = entries[0]
                                    values = entry['values']
                                    status_of_server = values['StatusReason']
                                    status_reson_of_server = values
                                    if status_of_server == "End of Life" and status_reson_of_server == "Obsolete":
                                        final_msg ="You are good to proceed with Reclaiming the server " + server_name + "."
                                        idempotent_obj.append("SUCCESS"+final_msg)
                                    else:
                                        server_deco =False
                                        final_msg = "The server "+server_name+" is Not in Deco in Progress status to reclaim it."+" Kindly check with application team"
                                        idempotent_obj.append("FAILRE"+final_msg)
                                elif len(entries)== 0:
                                    server_deco =False
                                    final_msg = "Unable to fetch cmdb status of server as duplicate entries exist but instance id doesnt match"
                                    idempotent_obj.append("FAILRE"+final_msg)
                                else:
                                    server_deco =False
                                    final_msg = "Unable to fetch cmdb status of server as duplicate entries exist with same instance id"
                                    idempotent_obj.append("FAILRE"+final_msg)
            # response = requests.post(url=logout_url, headers=headers)
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                              cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None
            result = str(response.status_code) + ' ' + response.reason
        except Exception as err: 
            server_deco =False
            final_msg = "Exception in CMDB FETCH module.Kindly check if inputs are valid :"+str(err)
            idempotent_obj.append("FAILRE"+final_msg)

    if server_deco == True:
        idempotent_obj = "SUCCESS"
    else:
        idempotent_obj = "FAILURE"

    return idempotent_obj


def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
        "conn_str":{"required":False, "type":"str", "default":""},
        "ci_list":{"required":True,"type":"dict"},
        "cmdb_server":{"required":True,"type":"str"},
        "user_name":{"required":True,"type":"str"},
        "pass_word":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = cmdb_fetch(conn_str=module.params["conn_str"],
                                          ci_list= module.params["ci_list"],
                                          cmdb_server= module.params["cmdb_server"],
                                          user_name= module.params["user_name"],
                                          pass_word= module.params["pass_word"])
        if create_entity_result:
            returnvalue["create_entity_result"] = create_entity_result
            returnvalue['changed'] = True
            # module.exit_json(**returnvalue)
        else:
            returnvalue["create_entity_result"] = create_entity_result
            # module.exit_json(**returnvalue)
        
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["create_entity_result"]="Exception occurred while creating entity.Kindly check. " +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()