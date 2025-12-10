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

def net(hostname,username,password,switch):                                 
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
    for x in switch:
        chan = ssh.invoke_shell()
        chan.send('ssh '+username+'@'+x+'\n')
        time.sleep(5)
        
        chan.send(password+'\n')
        time.sleep(5)

        chan.send('show version\n')
        time.sleep(5)
        out = chan.recv(999999999)
        time.sleep(5)    
    out = out.decode('utf-8')
    resp_o = switch
    try:
        if "Cisco" in out:
            resp_ven = 'cisco'
            return resp_ven
        elif "Arista" in out:
            if "muc-az" in switch:
                resp_ven = 'amn_arista'
                return resp_ven
            else:
                resp_ven = 'arista'
                return resp_ven
        else:
            chan.send('display version\n')
            time.sleep(5)
            out = chan.recv(999999999)
            time.sleep(5)
            if "HPE Comware" in out:
                resp_ven = 'hp'
                return resp_ven
            else:
                resp_ven = 'unknown'
                return resp_ven
    except Exception as err:
        resp_ven = err
        return resp_ven

    #resp = [resp_o, resp_s, resp_i, resp_o, resp_t, resp_i, resp_o, resp_e, resp_i]
    #print(resp)
    ssh.close() 
    #return resp               

    
#net('muccws11','no7da611','ptr1','Waltdisney#2025',['mucrtp404'])
def main():
    returnValue = dict()
    fields = {     
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}, 
        "switch":{"required":True, "type":"list"}             
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        resp_ven = net(module.params["hostname"],module.params["username"],module.params["password"],module.params["switch"])
                    
        returnValue["resp_ven"] = resp_ven             
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnValue["resp_ven"] = "[ERROR]" + str(err)
        module.exit_json(**returnValue)             

if __name__ == '__main__':
    main()
