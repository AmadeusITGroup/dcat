import time
from ansible.module_utils.basic import AnsibleModule
import paramiko

DOCUMENTATION = r'''
---
module: copy hponcfg package to target server

description: copy hponcfg package to target server

version_added: "1.0.0"

options:
    hostname:
        description: list of host
        required: true
        type: str
    
'''

EXAMPLES = r'''
    - name: "Custom module backup software removal"
      copy_package:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        password: "{{ password }}
        package: "{{ package }}"
      register: copy_status 
'''
RETURN = r'''
status:
    description: Returning the VM name.
    type: str 
    returned: always

'''

def file_copy(hostname,username,password,package):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,timeout=5)
    except Exception as e:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,**fallback_to_sha1)
            time.sleep(2)
        except Exception as e:
            pass
    time.sleep(2)
    sftp = ssh.open_sftp()
    time.sleep(2)
    localpath="packages/"+package
    remotepath="/home/"+username+"/"+package
    sftp.put(localpath, remotepath)
    sftp.close()
    ssh.close()
    status = "File Transfer Completed"
    return status

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True},
        "package":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = file_copy(module.params["hostname"],
                          module.params["username"],
                          module.params["password"],
                          module.params["package"])

        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[ERROR] Exception occurred during package transfer, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()