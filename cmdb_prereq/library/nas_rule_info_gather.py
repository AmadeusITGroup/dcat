import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule



DOCUMENTATION = r'''
---
module: nas_rule_info_gather

description: This module is used to gather information assocaited with the rules under the export policy. 

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
    - Leethu T.L (@pltl)
'''

EXAMPLES = r'''
    - name: "information gathering for recovery process"
      fetch_rule_nas:
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
        ip_addr: "{{ ip_addr }}"
        port_name: "{{ item }}"
      delegate_to: localhost
      register: port_rename_disable_output
      
'''
def fetch_rule_info(username,password,storage_box,v_server,policy_name,vm_name):
    try:
        rule_info_command="export-policy rule show -vserver "+v_server+" -policyname "+policy_name+" -clientmatch "+vm_name+"*"+" -fields ro,rw,superuser,anon,clientmatch"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(storage_box, username=username, password=password, port=22)
        time.sleep(3)
        # pylint: disable-next=unused-variable
        stdin,stdout,stderr = ssh_client.exec_command(rule_info_command)
        time.sleep(5)
        output = stdout.read().decode().strip()
        #print(output)

        if len(output) == 0 or re.search('There are no entries matching your query', output):
            time.sleep(5)
            msg = "There are no entries matching your query"
        else:
            msg = output

        ssh_client.close()
        return msg

    except Exception as err:  # pylint: disable=broad-except
        ssh_client.close()
        value = "Exception occurred: "+str(err)
        return value

def main():
    returnvalue = {}
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "storage_box":{"required":True,"type":"str"},
                "v_server":{"required":True,"type":"str"},
                "policy_name":{"required":True,"type":"str"},
                "vm_name":{"required":True,"type":"str"}
        }
    module = AnsibleModule(argument_spec = fields)

    try:
        username = module.params["username"]
        password = module.params["password"]
        storage_box = module.params["storage_box"]
        v_server = module.params["v_server"]
        policy_name = module.params["policy_name"]
        vm_name = module.params["vm_name"]
        rule_info_fetch =fetch_rule_info(username,password,storage_box,v_server,policy_name,vm_name)
        returnvalue["rule_info_output"] = rule_info_fetch
        module.exit_json(** returnvalue)

    except Exception as err:  # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
