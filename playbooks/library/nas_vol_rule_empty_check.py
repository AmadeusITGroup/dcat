import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule



DOCUMENTATION = r'''
---
module: port_rename_disable

description: This module is used to check if the rules are empty and fetching the volume information which is associated to the host. 

version_added: "1.0.0"

options:
    username:
        description: Username of service account used to interact with storgae box.
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
    - name: "Testing Port Rename and Disable module"
      fetch_rule_nas:
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
        ip_addr: "{{ ip_addr }}"
        port_name: "{{ item }}"
      delegate_to: localhost
      register: port_rename_disable_output
      
'''
def fetch_rule_empty(username,password,storage_box,v_server,policy_name):
    try:
        export_policy_cmd = "export-policy rule show -vserver " + v_server + " -policy "+ policy_name + " -fields policyname"
        volume_command = "volume show -vserver " + v_server + " -policy "+ policy_name + " -fields volume,policy"

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(storage_box, username=username, password=password, port=22)
        time.sleep(3)
        stdin,stdout,stderr = ssh_client.exec_command(export_policy_cmd)
        time.sleep(5)
        output = stdout.read().decode().strip()
        #print(output)

        if len(output) == 0 or re.search('There are no entries matching your query', output):
            stdin,stdout,stderr = ssh_client.exec_command(volume_command)
            time.sleep(5)
            output_export = stdout.read().decode().strip()
            list_output = list(output_export.split(" "))
            list_output = [i for i in list_output if i]
            del list_output[0 :10]
            res_vol = []
            for sub in list_output:
                res_vol.append(sub.replace("\r\n", ""))
            output_volume_name =  res_vol[1]
            msg = output_volume_name
            msg_output = "No Rules"
        else:
            msg = "Rules EXIST"
            msg_output = output

        ssh_client.close()
        return msg,msg_output

    except Exception as err: # pylint: disable=broad-except
        ssh_client.close()
        value = "Exception occurred: "+str(err)
        return value


#fetch_rule_empty(username,password,storage_box,v_server,policy_name)
def main():
    returnvalue = {}
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "storage_box":{"required":True,"type":"str"},
                "v_server":{"required":True,"type":"str"},
                "policy_name":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)

    try:
        username = module.params["username"]
        password = module.params["password"]
        storage_box = module.params["storage_box"]
        v_server = module.params["v_server"]
        policy_name = module.params["policy_name"]
        rule_vol_info_fetch  =fetch_rule_empty(username,password,storage_box,v_server,policy_name)
        returnvalue["vol_rule_output"] = rule_vol_info_fetch
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
