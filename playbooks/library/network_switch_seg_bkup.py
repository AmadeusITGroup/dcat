import paramiko
import re
import time
from ansible.module_utils.basic import AnsibleModule


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

def net(hostname,ph_server,username,password,switch):                                 
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
    time.sleep(5) 
    if (switch != ""):
        chan = ssh.invoke_shell()
        chan.send('ssh '+username+'@'+switch+'\n')
        time.sleep(5)
        chan.send(password+'\n')
        time.sleep(5)
        chan.send('sh interface status | include '+ph_server+'\n')
        time.sleep(5)
        out = chan.recv(999999999)
        time.sleep(5)
    else:
        stat = "No switches for the "+ ph_server         
    out = out.decode('utf-8')
    print(out)
    resp_o = switch
    lines = out.split('\n')
    output = []
    current_port = None
    for line in lines:
        port_match = re.search(r'(Eth\d+/\d+|Et\d+/\d+|Po\d+)', line)
        status_match = re.search(r'connected', line)
        if port_match:
            current_port = port_match.group(1)
            if current_port.startswith('Eth'):
                current_port = 'Ethernet' + current_port[3:]
            elif current_port.startswith('Et'):
                current_port = 'Ethernet' + current_port[2:]           
        if current_port and status_match:
            output.append(f'server : {ph_server}\nswitch : {resp_o}\nport : {current_port}\nstatus : connected\n')
    stat = '\n'.join(output)  
    ssh.close()
    return stat  


def main():
    returnValue = dict()
    fields = {     
        "hostname":{"required":True, "type":"str"},
        "ph_server":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}, 
        "switch":{"required":True, "type":"list"}             
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        stat = net(module.params["hostname"],module.params["ph_server"],module.params["username"],module.params["password"],module.params["switch"])
                    
        returnValue["stat"] = stat              
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnValue["stat"] = "[ERROR] No switches for the "+ module.params["ph_server"]  + str(err)
        module.exit_json(**returnValue)             

if __name__ == '__main__':
    main()
