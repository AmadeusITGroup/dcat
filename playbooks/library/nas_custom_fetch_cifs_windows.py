import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: 

description: This module is used to fetch share informaton associated to the host. 

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
    vm_name:
        description: name of the input vm .
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

def fetch_cifs_nas(username,password,storage_box,vm_name):
    try:
        fetch_cmd = "cifs share access-control show -user-or-group MUCMSPDOM\\" +  vm_name + "$" + " -fields vserver,share,user-group-type,permission,user-or-group"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(storage_box, username=username, password=password, port=22)
        time.sleep(3)
        stdin,stdout,stderr = ssh_client.exec_command(fetch_cmd)
        time.sleep(5)
        output = stdout.read().decode().strip()
        #print(output)

        if len(output) == 0 or re.search('There are no entries matching your query', output):
            #print(output)
            value = "no entries"
        else:
            list_out = list(output.split(" "))
            list_out = [i for i in list_out if i]
            #print(list_out)
            #print(list_out[-1])
            del list_out[0 :14]
            if list_out[-1] == "displayed." :
                del list_out[-1]
                del list_out[-1]
                del list_out[-1]
                del list_out[-1]
            else:
                value = list_out
            res = []
            for sub in list_out:
                res.append(sub.replace("\r\n", ""))
            new_list =[]
            i=0
            while i<len(res):
                new_list.append(res[i:i+5])
                i+=5
            #print(new_list)
            value =  new_list
            #value =  output
        ssh_client.close()
        return value,output
        #print(value,output)

    except Exception as err:  # pylint: disable=broad-except
        ssh_client.close()
        output= ""
        value = "Exception occurred: "+str(err)
        return value,output
       #print(value,output)

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
        share_info_fetch  =fetch_cifs_nas(username,password,storage_box,vm_name)
        returnvalue["share_output"] = share_info_fetch
        module.exit_json(** returnvalue)

    except Exception as err:  # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
