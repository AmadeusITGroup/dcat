import time
import paramiko
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: nfs_info_fetch

description: Checking if the linux servers has nfs mounted by taking ssh connection to the server.

version_added: "1.0.0"

options:
    hostname:
        description: name of the server 
        required: true
        type: str
    
author:
    - Leethu T.L (@pltl)
'''

EXAMPLES = r'''
    - name: "Custom module to check if nas is mounted on server"
      nfs_mount_info:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        key_filename: "{{ key_filename }}"
      register: nfs_mount_check  
'''


def nfs_info_fetch(hostname,username,key_filename):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=hostname,username=username,key_filename=key_filename,port=22)
        except Exception as e:
            try:
                fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
                ssh.connect(hostname=hostname, username=username, key_filename=key_filename, port=22, **fallback_to_sha1)
            except Exception as e:
                return f"[Exception] Connection failed: {e}"
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command(" cat /etc/fstab | grep -i nfs | grep -v '#'")
        time.sleep(2)
        info_output = stdout.readlines()
        #print(info_output)
        if len(info_output) == 0 :
            time.sleep(5)
            msg_nfs = "no nfs mounted"
        else:
            msg_nfs = "NFS present"

        ssh.close()
        return msg_nfs

    except Exception as err:  # pylint: disable=broad-except
        ssh.close()
        value = "Exception occurred: "+str(err)
        return value


def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "key_filename":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = nfs_info_fetch(module.params["hostname"],
                                module.params["username"],
                                module.params["key_filename"])

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err:  # pylint: disable=broad-except
        print("Exception occurred : " + str(err))
        module.fail_json(**returnvalue)

if __name__ == '__main__':
    main()
