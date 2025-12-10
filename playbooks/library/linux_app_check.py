'''
This program validates the linux process existence
'''

import time
import paramiko
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: Application Validation check on linux servers

description: Check application exists on linux server prior DECO process.

version_added: "1.0.0"

options:
    app_name:
        description: App Name to be checked on the server.
        required: true
        type: str
    host:
        description: Linux Server on which application validation to be performed.
        required: true
        type: str
    username:
        description: Username of service account used to interact LINUX server.
        required: true
        type: str
    key_filename:
        description: Key File path to use the private key to authenticate to LINUX server
        required: true
        type: str

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          linux_app_check:
            app_name: "{{obe_application_name.OBE_application_name}}"
            host: "{{inventory_hostname}}"
            username: "{{ username }}"
            key_filename: "{{ key_filename }}"
          register: OBE_linux_status
          delegate_to: localhost
'''
def app_check(app_name,host,username,key_filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host,username=username,key_filename=key_filename,port=22)
    except Exception as e:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=host, username=username, key_filename=key_filename, port=22, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"
    time.sleep(2)
    cmd="pgrep -f sei_agent"
    # pylint: disable-next=unused-variable
    stdin, stdout, stderr = ssh.exec_command(cmd)
    process= stdout.readlines()
    if process:
        result = "sei_agent is running with id "+ str(process)
    else:
        result = "NA"
    ssh.close()
    return result


def main():
    returnvalue = {}
    fields = {
        "app_name":{"required":True, "type":"str"},
        "host":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str"},
        "key_filename":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = app_check(module.params["app_name"],
                           module.params["host"],
                           module.params["username"],
                           module.params["key_filename"])
        returnvalue["status"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
