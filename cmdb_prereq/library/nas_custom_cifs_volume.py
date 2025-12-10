import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule
DOCUMENTATION = r'''
---
module: 

description: This module is used to fetch volume and acl informaton associated to the host. 

version_added: "1.0.0"

options:
    username:
        description: Username of service account used to interact with storage box.
        required: true
        type: str
    password:
        description: Password of service account used to interact with storage box.
        required: true
        type: str
    storage_box:
        description: storage box where the shares for the server is configured.
        required: true
        type: str
    system_name:
        description: name of the system account with input name in it .
        required: true
        type: str
    share_name  :
        description: name of the share which has the system account.
        required: true
        type: str            
author:
    - Leethu T L (@pltl)
'''

EXAMPLES = r'''
    - name: "fetch share informaton associated to the host module"
      :
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
        ip_addr: "{{ ip_addr }}"
        port_name: "{{ item }}"
      delegate_to: localhost
      register: 
      
'''

def fetch_cifs_nas(username,password,storage_box,system_name,share_name):
    vol_name=""
    fetch_cmd ="cifs share show -acl "+system_name+"*"+" -share-name "+share_name+" -fields volume "
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(storage_box, username=username, password=password, port=22)
    time.sleep(3)
    stdin,stdout,stderr = ssh_client.exec_command(fetch_cmd)
    time.sleep(5)
    output = stdout.read().decode().strip()
    if len(output) == 0 or re.search('There are no entries matching your query', output):
        vol_name = "no entries for volume"
    else:
        list_out = list(output.split(" "))
        list_out = [i for i in list_out if i]
        del list_out[0 :10]
        res = []
        for sub in list_out:
            res.append(sub.replace("\r\n", ""))
        value =  res
        vol_name = value[2]
    ssh_client.close()
    return vol_name

def main():
    returnvalue = {}
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "storage_box":{"required":True,"type":"str"},
                "system_name":{"required":True,"type":"str"},
                "share_name":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)
    try:
        username = module.params["username"]
        password = module.params["password"]
        storage_box = module.params["storage_box"]
        system_name = module.params["system_name"]
        share_name = module.params["share_name"]
        share_info_fetch  =fetch_cifs_nas(username,password,storage_box,system_name,share_name)
        returnvalue["share_output"] = share_info_fetch
        module.exit_json(** returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
