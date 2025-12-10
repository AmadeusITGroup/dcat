import urllib.parse
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None

def get_owner(conn_str,server_name,cmdb_server,user_name,pass_word,instance_id):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    entry_url = cmdb_server + "/api/arsys/v1/entry"
    #### Field names and its values need to be changed wrt deco prcocess ###
    fieldname_1 = 'AssetLifecycleStatus'  ###End of Life   #'Description'
    fieldname_2 ='StatusReason' ###Obsolete
    fieldname_3 = 'AdminIP'
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
    
    # Login
    JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                               cmdb_server=cmdb_server,
                                               password=pass_word)
    if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
        final_msg_cmdb = "An error occurred : " + str(JWT_AUTH_TOKEN)
        JWT_AUTH_TOKEN = None
        return final_msg_cmdb
    headers = {
            'Content-Type': 'application/json',
                'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
            }
    query = qprefix + ' and  Name="' + server_name + '"'
    encoded_query = urllib.parse.quote(query)
    #fields = 'Name,RequestId,AssetID,' + fieldname_1  +' , ' + fieldname_2 +' , ' + fieldname_3
    parameters = 'q=' + encoded_query  #+ '&fields=values(' + fields + ')'
    url = entry_url + '/BMC.CORE:BMC_ComputerSystem?' + parameters
    response = requests.get(url=url, headers=headers)
    # Logout
    if JWT_AUTH_TOKEN is not None:
        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                      cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
        JWT_AUTH_TOKEN = None
    result = str(response.status_code) + ' ' + response.reason
    if response.status_code != 200:
        raise Exception("Error occured while fetching info: {}".format(response))
    result = response.json()
    # response = requests.post(url=logout_url, headers=headers)
    logout = str(response.status_code) + ' ' + response.reason
    data=result['entries'][0]['values']['OperatedBy']
    if data:
     return data
    else:
      data = "NA"
      return data

def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":False, "type":"str", "default":""},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str"},
         "pass_word":{"required":True, "type":"str"},
         "instance_id":{"required":False, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        group_by_owner = get_owner(conn_str=module.params["conn_str"],
                                   server_name = module.params["server_name"],cmdb_server= module.params["cmdb_server"],user_name= module.params["user_name"],pass_word= module.params["pass_word"],instance_id= module.params["instance_id"])
        returnvalue["Status"] = group_by_owner
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = "Exception occurred while filtering groups.Kindly check. " + str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()