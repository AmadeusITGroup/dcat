import time
from ansible.module_utils.basic import AnsibleModule
import paramiko
import datetime

DOCUMENTATION = r'''
---
module: nvme_cleanup

description: Checking if the linux servers has nvme/fusion io present by taking ssh connection to the server.

version_added: "1.0.0"

options:
    hostname:
        description: name of the server 
        required: true
        type: str
    
author:
    - Krishna (@pvraja)
'''

EXAMPLES = r'''
    - name: "Custom module to check if nvme/fusion io is mounted on server"
      nvme_cleanup:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        key_filename: "{{ key_filename }}"                           
      register: output_nvme_cleanup
'''

def checklin(hostname,username,password):
    cmd1 = '''sudo -i pvs --noheadings --options pv_name,vg_name | awk '$2=="vg00"{split($1,a,/[0-9\/]/);print a[3]}' > /tmp/exclude_devs'''
    cmd2 = '''sudo -i mount | awk '$3=="/boot"{split($1,a,/[0-9\/]/);print a[3]}' >>/tmp/exclude_devs'''
    cmd3 = '''sudo -i lsblk -r | grep -wvf /tmp/exclude_devs | awk '$6=="disk"{print $1}' '''    
    idempotent_obj = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            try:
                ssh.connect(hostname,username=username,key_filename=password,port=22)
            except Exception:
                fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
                ssh.connect(hostname, username=username, key_filename=password, port=22, **fallback_to_sha1)
            stdin, stdout, stderr = ssh.exec_command(cmd1)
            print(stdout.read().decode())
            stdout.channel.recv_exit_status()
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command(cmd2)
            stdout.channel.recv_exit_status()
            time.sleep(2)
            stdin, stdout, stderr = ssh.exec_command(cmd3)
            new_out = stdout.readlines()
            disks = [line.strip() for line in new_out if line.strip()]
            for nvme_storage in disks:
               if "fio" in nvme_storage or "nvm" in nvme_storage:
                    idempotent_obj.append(nvme_storage+" present")
               else:
                   idempotent_obj.append(nvme_storage+" absent")
            return idempotent_obj
        except Exception as e:
            return "Failure in running the commands" + str(e)
    except Exception as e:
        return "Failure " + str(e)


def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = checklin(module.params["hostname"],
                          module.params["username"],
                          module.params["password"])

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "Exception occurred during ssh, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
