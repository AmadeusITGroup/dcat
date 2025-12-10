from ansible.module_utils.basic import *
import paramiko
import re
import time

DOCUMENTATION = r'''
---
module: backup_removal_linux

description: Removing backup packages "TIVsm-BA" and "TIVsm-API"

version_added: "1.0.0"

options:
    hostname:
        description: list of host for package removal.
        required: true
        type: str
    
author:
    - Thineshkumar R (@thr)
'''

EXAMPLES = r'''
    - name: "Custom module backup software removal"
      backup_removal_linux:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        key_filename: "{{ key_filename }}"
      register: backup_package  
'''
RETURN = r'''
status:
    description: Returning the status by length of the list index.
    type: len 
    returned: always

'''

def net(hostname,ph_server,username,password):                                 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    try:
        ssh.connect(hostname=hostname,username=username,password=password,port=22)
    except Exception:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname, username=username, password=password, port=22, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"     
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('config '+ ph_server +' | grep run')    
    time.sleep(2)
    sw_name = (stdout.readlines())
    ssh.close()
    return sw_name


def main():
    returnValue = dict()
    fields = {     
        "hostname":{"required":True, "type":"str"},
        "ph_server":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}             
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        sw_name = net(module.params["hostname"],module.params["ph_server"],module.params["username"],module.params["password"])
                    
        returnValue["sw_name"] = sw_name              
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnvalue["sw_name"] = "[ERROR]" + str(err)
        module.exit_json(**returnvalue)           

if __name__ == '__main__':
    main()
