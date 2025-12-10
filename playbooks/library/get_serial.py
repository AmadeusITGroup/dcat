import time
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

def checklin(hostname,username,password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname,username=username,key_filename=password,port=22)
    except Exception as e:
        try:
          fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
          ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,**fallback_to_sha1)
          time.sleep(2)
        except Exception as e:
          pass
    time.sleep(2)
    session = ssh.get_transport().open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    time.sleep(2)
    session.exec_command("sudo cat /sys/class/dmi/id/product_serial")
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    #stdin.write(password + '\n')
    stdin.flush()
    time.sleep(2)
    name = stdout.readlines()
    data = name[0].strip()
    # time.sleep(2)
    # stdin, stdout, stderr = ssh.exec_command(command)
    time.sleep(2)
    #data = stdout.readlines()
    #data = name[0].split("=")[1].split("(string)")[0].replace("'","").strip()
    if data:
      name= data
    else:
      name = "ERROR"
    ssh.close()
    return name

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = checklin(module.params["hostname"],
                          module.params["username"],
                          module.params["password"]
                            )

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "ERROR : Exception occurred during ssh, ERROR : "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
