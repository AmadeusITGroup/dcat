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

def checklin(hostname, ilo_url, ilo_username, ilo_password, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, username=username, key_filename=password, port=22, timeout=5)
    except Exception:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname, username=username, key_filename=password, port=22, timeout=5, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"

    try:
        if "poweroff" in command or "shutdown" in command:
            # Send shutdown command
            ssh.exec_command(command)
            ssh.close()  # Close SSH early after sending the command

            # Wait up to 900 seconds, checking every second
            for i in range(90):
                ilo_ssh = paramiko.SSHClient()
                ilo_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ilo_ssh.connect(hostname=ilo_url,username=ilo_username,password=ilo_password,port=22)
                time.sleep(2)
                stdin, stdout, stderr = ilo_ssh.exec_command("power")
                power_status_output = stdout.read().decode()
                ilo_ssh.close()
                
                if "Off" in power_status_output:
                    return "Shutdown successfully completed, validated with iLO."
                time.sleep(10)

            return "Shutdown command sent, but iLO never reported power off within timeout."

        # If not shutdown command
        session = ssh.get_transport().open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        time.sleep(2)
        session.exec_command(command)
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stdin.flush()
        time.sleep(2)
        output = stdout.readlines()
        ssh.close()

        return output if output else "Command executed but no output returned."

    except Exception as e:
        ssh.close()
        return f"[Exception] during command execution: {e}"

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "ilo_url": {"required":False, "type":"str"},
        "ilo_username": {"required":False, "type":"str","no_log":True},
        "ilo_password": {"required":False, "type":"str","no_log":True},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True},
        "command":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = checklin(module.params["hostname"], module.params["ilo_url"], module.params["ilo_username"], module.params["ilo_password"],
                          module.params["username"],module.params["password"],module.params["command"])

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "Exception occurred during ssh, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
