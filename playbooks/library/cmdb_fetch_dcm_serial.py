import urllib.parse
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None

def get_serial_numbers(conn_str,server_name,cmdb_server,user_name,pass_word):
    #try:
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ

    entry_url = cmdb_server + "/api/arsys/v1/entry"
    qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'

    
    # Login
    JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                               cmdb_server=cmdb_server,
                                               password=pass_word)
    if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != 200:
        final_msg_cmdb = 'An error occurred, Login failed with error: ' + str(JWT_AUTH_TOKEN)
        JWT_AUTH_TOKEN = None
        return final_msg_cmdb
    # auth_token = response.text

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
        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                      cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
        JWT_AUTH_TOKEN = None
    if response.status_code != 200:
        raise Exception("Failed to fetch data for server: " + server_name)
    entries = response.json()['entries']
    for entry in entries:
        serial_number = entry['values']['SerialNumber']
        host = entry['values']['Name']
        res = serial_number
    # except Exception as e:
    #     print("An error occurred:", str(e))
    # finally:
    if JWT_AUTH_TOKEN is not None:
        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                      cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
        JWT_AUTH_TOKEN = None
    # requests.post(url=logout_url, headers=headers)
    return res

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
        cmdb_serial_number = get_serial_numbers(conn_str=module.params["conn_str"],
                                                server_name=module.params["server_name"],cmdb_server= module.params["cmdb_server"],user_name= module.params["user_name"],pass_word= module.params["pass_word"])
        returnvalue["Status"] = cmdb_serial_number
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

if __name__ == "__main__":
    run_module()
