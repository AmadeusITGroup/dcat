import time, datetime
from ansible.module_utils.basic import AnsibleModule
import paramiko

DOCUMENTATION = r'''
---
module: ssh_check_linux

description: validating SSH connection

version_added: "1.0.0"

options:
    hostname:
        description: list of host
        required: true
        type: str
    
author:
    - Thineshkumar R (@thr)
'''

EXAMPLES = r'''
    - name: "Custom module backup software removal"
      ssh_check_linux:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        key_filename: "{{ key_filename }}"
      register: connect 
'''
RETURN = r'''
status:
    description: Returning the VM name.
    type: str 
    returned: always

'''

def checklin(hostname,username,key_filename):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=hostname,username=username,key_filename=key_filename,port=22,timeout=5)
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command('hostname')
            time.sleep(2)
            name = stdout.readlines()
            ssh.close()
            return name
        except Exception as e:
            try:
                fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
                ssh.connect(hostname=hostname,username=username,key_filename=key_filename,port=22,timeout=5,**fallback_to_sha1)
                time.sleep(2)
                stdin, stdout, stderr = ssh.exec_command('hostname')
                time.sleep(2)
                name = stdout.readlines()
                ssh.close()
                return name
            except Exception as e:
                time.sleep(2)
                ssh.close()
                now = datetime.datetime.now()
                return "SSH check completed and server not accessible - TIME: " + str(now)
    except Exception as e:
        now = datetime.datetime.now()
        return "SSH check Failed for host - "+ hostname +" TIME: " + str(now)
  
def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "key_filename":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = checklin(module.params["hostname"],
                          module.params["username"],
                          module.params["key_filename"])

        returnvalue["status"] = status
        returnvalue["msg"] = "Successfully ssh into the vm: " + module.params["hostname"]
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "Exception occurred during ssh, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()