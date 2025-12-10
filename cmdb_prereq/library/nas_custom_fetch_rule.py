import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: nas_custom_fetch_rule

description: This module is used to fetch rule and export policy details associated to the host and its IP. 

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
    ip_addr:
        description: IP address of the switch which is associated to the host.
        required: true
        type: str
    port_name:
        description: Ports which is associated to the host.
        required: true
        type: str
          
author:
    - Leethu T L (@pltl)
'''

EXAMPLES = r'''
    - name: "fetching rule and export policy information module"
      fetch_rule_nas:
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
        ip_addr: "{{ ip_addr }}"
        port_name: "{{ item }}"
      delegate_to: localhost
      register: port_rename_disable_output
      
'''

def fetch_rule_nas(username,password,storage_box,vm_name):
    try:
        rename_cmd = "export-policy rule show -clientmatch " + vm_name + "*"+ " -fields vserver"
        print(rename_cmd)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(storage_box, username=username, password=password, port=22)
        time.sleep(3)
        stdin,stdout,stderr = ssh_client.exec_command(rename_cmd)
        time.sleep(5)
        output = stdout.read().decode().strip()

        if len(output) == 0 or re.search('There are no entries matching your query', output):
            value = output
        else:
            list_out = list(output.split(" "))
            list_out = [i for i in list_out if i]
            # print(list_out)
            # print(list_out[-1])
            del list_out[0 :10]
            if list_out[-1] == "displayed." :
                del list_out[-1]
                del list_out[-1]
                del list_out[-1]
                del list_out[-1]
            else:
                #print(list_out)
                value = list_out
            res = []
            for sub in list_out:
                res.append(sub.replace("\r\n", ""))
            new_list =[]
            i=0
            while i<len(res):
                new_list.append(res[i:i+3])
                i+=3
            #print(new_list)
            value =  new_list
        ssh_client.close()
        return value

    except Exception as err: # pylint: disable=broad-except
        ssh_client.close()
        value = "Exception occurred: "+str(err)
        return value


#fetch_rule_nas(username,password,storage_box,vm_name)
def main():
    returnvalue = {}
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "storage_box":{"required":True,"type":"str"},
                "vm_name":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)

    try:
        username = module.params["username"]
        password = module.params["password"]
        storage_box = module.params["storage_box"]
        vm_name = module.params["vm_name"]
        rule_info_fetch  =fetch_rule_nas(username,password,storage_box,vm_name)
        returnvalue["rule_output"] = rule_info_fetch
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
