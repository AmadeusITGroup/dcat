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

def checklin(hostname,username,password,command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname,username=username,password=password)
    except Exception:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname, username=username, password=password, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"
    session = ssh.get_transport().open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    time.sleep(2)
    session.exec_command("sudo bash -c \"" + command + "\"")
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    stdin.write(password + '\n')
    stdin.flush()
    time.sleep(2)
    name = stdout.readlines()
    ssh.close()
    return name

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "command":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = checklin(module.params["hostname"],
                          module.params["username"],
                          module.params["password"],
                          module.params["command"])

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "Exception occurred during ssh, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()