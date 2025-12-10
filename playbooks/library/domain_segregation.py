import urllib.parse
import requests
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
 
def server_segregation(conn_str,server_name, cmdb_server, user_name, pass_word):
    #returnvalue = {}
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    try:
        # TODO: Remove the urls:
        # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
        # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
        entry_url = cmdb_server + "/api/arsys/v1/entry"
        qprefix = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0)'
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
            final_msg = 'could not get server CI: ' + JWT_AUTH_TOKEN
            JWT_AUTH_TOKEN = None
            raise Exception(final_msg)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
       
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
            domain = "Error : Failed to fetch data for server: " + server_name
            raise Exception(domain)
        entries = response.json()['entries']
        if entries:
            server_domain  = entries[0]['values']['Domain']
            if server_domain == "muc.msp.net":
                domain ="MUCMSP"
            elif server_domain == "iis.net":
                domain = "IIS"
            # response = requests.post(url=logout_url, headers=headers)
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                            cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None
        if not entries:
            domain = "Server not found in CMDB: " + server_name
            # response = requests.post(url=logout_url, headers=headers)
            if JWT_AUTH_TOKEN is not None:
                logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                            cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
                JWT_AUTH_TOKEN = None
        return domain
    except Exception as e:
        domain = "error: "+str(e)
        # response = requests.post(url=logout_url, headers=headers)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                        cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        return domain
        #return "error: " + str(e)
 
 
# mucdomain, iisdomain = server_segregation(server_name, cmdb_server, user_name, pass_word)
# print("MUC Domain servers:", mucdomain)
# print("IIS Domain servers:", iisdomain)
 
 
# # result = server_segregation(server_name, cmdb_server, user_name, pass_word)
# # print("Function output:")
# # print(result)
 
def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str": {"required": True, "type": "str"},
         "server_name":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str","no_log":True},
         "pass_word":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    Data = "NA"
    try:
        Data = server_segregation(conn_str=module.params["conn_str"],server_name=module.params["server_name"],cmdb_server= module.params["cmdb_server"],user_name= module.params["user_name"],pass_word= module.params["pass_word"])
        returnvalue["Status"] = Data
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                        cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = Data
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                        cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
 
if __name__ == "__main__":
    run_module()