from ansible.module_utils.basic import *
import paramiko
import time


def san_sw(username,password,ipaddr):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    try:
        ssh.connect(hostname=ipaddr, username=username, password=password)
    except Exception:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=ipaddr, username=username, password=password, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"
    time.sleep(1)
    stdin,stdout,stderr = ssh.exec_command("switchName")
    time.sleep(2)
    status = stdout.readlines()
    swname = ''.join(map(str, status)).rstrip('\n')   
    ssh.close()
    return swname
    

def main():
    returnvalue = dict()
    fields = {     
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True},
        "ipaddr":{"required":True, "type":"str"}               
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        swname = san_sw(module.params["username"],module.params["password"],module.params["ipaddr"])          
        returnvalue["swname"] = swname
        returnvalue["msg"] = "[INFO] Successfully ssh to SAN box "+ swname
        returnvalue["ip"] = "[INFO] Successfully ssh to SAN box "+ module.params["ipaddr"]  
        module.exit_json(** returnvalue)                  
        
    except Exception as err:
        returnvalue["msg"] = "[ERROR] Failed to ssh " + module.params["ipaddr"] + str(err)
        module.exit_json(**returnvalue)           

if __name__ == '__main__':
    main()
