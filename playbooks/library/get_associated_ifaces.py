from ansible.module_utils.basic import AnsibleModule
import requests
import urllib
import json
import sys
from ansible.module_utils.cmdb.helpers_for_cmdb import login_cmdb, logout_cmdb
JWT_AUTH_TOKEN, CMDB_USER_OBJ = None, None
DOCUMENTATION = r'''
---
module: 

description: Fetching Hosted Access Point details from CMDB.

version_added: "1.0.0"

options:
    servername:
        description: Name of Server which is deleted or shutdown.
        required: true
        type: str

    ipadddr:
        description: ipaddress of the server
        required: true
        type: str

    cmdb_server:
        description: Server part of the API URL.
        required: true
        type: str
                
    USERNAME:
        description: Username for the CMDB login.
        required: true
        type: str
        
    Password:
        description: Password for the CMDB login.
        required: true
        type: str   
        
    
author:
    - Prashanth K(@ppk1)
'''

def get_ifaces(conn_str,servername,ipaddr,cmdb_server,username,password):
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    # TODO: Remove the urls:
    # login_url = "http://" + cmdb_server +":8008/api/jwt/login"
    # logout_url = "http://" + cmdb_server +":8008/api/jwt/logout"
    entry_url = cmdb_server + "/api/arsys/v1/entry"
    FIELDNAME_1 = 'AssetLifecycleStatus'
    FIELDNAME_2 ='StatusReason'
    # TODO: Remove Login details:
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # body = {'username': user_name, 'password': pass_word}
    # response = requests.post(url=login_url, data=body, headers=headers)
    # result = str(response.status_code) + ' ' + response.reason
    # auth_token = response.text
    
    # Login
    JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                               cmdb_server=cmdb_server,
                                               password=password)
    
    if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
        final_msg_cmdb = "Unable to get server CI: " + str(JWT_AUTH_TOKEN)
        JWT_AUTH_TOKEN = None
        return final_msg_cmdb
    
    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
    inst_id = []
    query = 'Name="' + ipaddr + '" and SystemName="' + servername + '"'
    encoded_query = urllib.parse.quote(query)
    parameters = 'q=' + encoded_query  + '&fields'
    url = entry_url + '/BMC.CORE:BMC_IPEndpoint?' + parameters
    response = requests.get(url=url, headers=headers)
    # Logout
    if JWT_AUTH_TOKEN is not None:
        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                 cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
        JWT_AUTH_TOKEN = None
    result = str(response.status_code) + ' ' + response.text
    if response.status_code != requests.codes.ok:
        raise ValueError('could not get server CI: '+result)
    result = response.json()
    for data in result['entries']:
         inst_id.append((data['values']['RelLeadInstanceId']))
    #------------------------------------------------------------------------------------
    dest_inst=[]
    for id in inst_id:
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=password)
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
            final_msg_cmdb = "Unable to get server CI: " + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            raise Exception(final_msg_cmdb)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
        dest_inst=[]
        query= 'Source.InstanceId="' + id + '" and Name="HOSTEDACCESSPOINT"'
        encoded_query = urllib.parse.quote(query)
        parameters = 'q=' + encoded_query  + '&fields'
        url = entry_url + '/BMC.CORE:BMC_BaseRelationship?' + parameters
        response = requests.get(url=url, headers=headers)
        # Logout
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        result = str(response.status_code) + ' ' + response.text
        if response.status_code != requests.codes.ok:
            raise ValueError('could not get server CI: '+result)
        result = response.json()
        for data in result['entries']:
            dest_inst.append(data['values']['Destination.InstanceId'])
    # #------------------------------------------------------------------------------------
    ip=[]
    for data in dest_inst:
        JWT_AUTH_TOKEN, CMDB_USER_OBJ = login_cmdb(conn_str=conn_str,
                                                   cmdb_server=cmdb_server,
                                                   password=password)
        if "NO LOGIN" in JWT_AUTH_TOKEN:  # response.status_code != requests.codes.ok:
            final_msg_cmdb = "Unable to get server CI: " + str(JWT_AUTH_TOKEN)
            JWT_AUTH_TOKEN = None
            raise Exception(final_msg_cmdb)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'AR-JWT ' + JWT_AUTH_TOKEN
        }
        query= 'InstanceId="' + data + '"'
        encoded_query = urllib.parse.quote(query)
        parameters = 'q=' + encoded_query  + '&fields'
        url = entry_url + '/BMC.CORE:BMC_IPEndpoint?' + parameters
        response = requests.get(url=url, headers=headers)
        # Logout
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                     cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
            JWT_AUTH_TOKEN = None
        result = str(response.status_code) + ' ' + response.text
        if response.status_code != requests.codes.ok:
            raise ValueError('could not get server CI: '+result)
        result = response.json()
        for data in result['entries']:
            if data['values']['Address'] != ipaddr:
              ip.append(data['values']['Address'])
    # response = requests.post(url=logout_url, headers=headers)
    if JWT_AUTH_TOKEN is not None:
        logout_cmdb(cmdb_server=cmdb_server, auth_token=JWT_AUTH_TOKEN,
                                 cmdb_object=CMDB_USER_OBJ, conn_str=conn_str)
        JWT_AUTH_TOKEN = None
    # result = str(response.status_code) + ' ' + response.text
    if not ip:
      return "[INFO], No interfaces found for host: " + servername
    else:
      return ip

def run_module():
    global JWT_AUTH_TOKEN, CMDB_USER_OBJ
    fields = {
         "conn_str":{"required":False, "type":"str", "default":""},
         "servername":{"required":True, "type":"str"},
         "ipaddr":{"required":True, "type":"str"},
         "cmdb_server":{"required":True, "type":"str"},
         "username":{"required":True, "type":"str","no_log":True},
         "password":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        result = get_ifaces(conn_str=module.params["conn_str"],
                            servername = module.params["servername"],
                                  ipaddr = module.params["ipaddr"],
                                  cmdb_server= module.params["cmdb_server"],
                                  username= module.params["username"],
                                  password= module.params["password"]
                                  )
        returnvalue["ifaces"] = result
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["ifaces"]="[ERROR], Exception occurred while fetching associated interfaces from CMDB.Kindly check." +str(err)
        if JWT_AUTH_TOKEN is not None:
            logout_cmdb(cmdb_server=module.params["cmdb_server"], auth_token=JWT_AUTH_TOKEN,
                          cmdb_object=CMDB_USER_OBJ, conn_str=module.params["conn_str"])
            JWT_AUTH_TOKEN = None
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()