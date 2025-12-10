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
    for x in switch:
        chan = ssh.invoke_shell()
        chan.send('ssh '+username+'@'+x+'\n')
        time.sleep(5)
        
        chan.send(password+'\n')
        time.sleep(5)

        chan.send('sh interface status | include '+ph_server+'\n')
        time.sleep(5)
        out = chan.recv(999999999)
        time.sleep(5)    
    out = out.decode('utf-8')
    resp_i = ph_server
    resp_o = switch
    pat_eth = r'E[a-z]+[0-9]+/[0-9]+'
    resp_se = re.findall(pat_eth, out)
    if resp_se == []:
        pat_eth = r'E[a-z]+[0-9]+'
        resp_se = re.findall(pat_eth, out)        
        resp_s = []
        for i in resp_se:
            resp_s.append(i)
    else:
        resp_s = []
        for i in resp_se:
            resp_s.append(i)   
    pat_po = r'Po[0-9]+'             
    resp_th = re.findall(pat_po, out)
    resp_t = []
    for j in resp_th:
        resp_t.append(j)     
    pat_err = 'Permission denied'       
    resp_er = re.findall(pat_err, out)
    resp_e = []
    for k in resp_er:
        resp_e.append(k)    
    # resp_o = ','.join(map(str, resp_o))
    resp_s = ','.join(map(str, resp_s))
    resp_t = ','.join(map(str, resp_t))
    resp_e = ','.join(map(str, resp_e)) 
    resp_s = re.sub(r"E[a-z]+", "Ethernet", resp_s)

    resp = [resp_o, resp_s, resp_i, resp_o, resp_t, resp_i, resp_o, resp_e, resp_i]
    #print(resp)
    ssh.close() 
    return resp               

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
        resp = net(module.params["hostname"],module.params["ph_server"],module.params["username"],module.params["password"],module.params["switch"])
                    
        returnValue["resp"] = resp             
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnvalue["resp"] = "[ERROR]" + str(err)
        module.exit_json(**returnvalue)             

if __name__ == '__main__':
    main()
