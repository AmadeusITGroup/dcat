#!/usr/bin/env python

import paramiko
from ansible.module_utils.basic import AnsibleModule

# SSH connection wrapper with SHA1 fallback
def ssh_connect(host, username, key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host, username=username, key_filename=key_path, timeout=10)
    except Exception:
        # Fallback for older servers with only SHA1 support
        fallback_opts = {"disabled_algorithms": {"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]}}
        ssh.connect(hostname=host, username=username, key_filename=key_path, timeout=10, **fallback_opts)
    return ssh

# Function to SSH and check the mount point
def check_mount_and_dirs(hostname, username, key_path, mount_point):
    try:
        success_list = []
        failed_list = []
        for host in hostname:
            ssh = ssh_connect(host, username, key_path)

            # Check if the mount point exists
            stdin, stdout, stderr = ssh.exec_command(f"test -d {mount_point} && echo 'exists' || echo 'not_exists'")
            result = stdout.read().decode().strip()

            if result == 'exists':
                stdin, stdout, stderr = ssh.exec_command(f"find {mount_point} -maxdepth 1 -type d -name '[a-z][a-z][a-z]'")
                dirs = stdout.read().decode().splitlines()
                if dirs:
                    for dir_path in dirs:
                        stdin, stdout, stderr = ssh.exec_command(f"ls -A {dir_path} | grep '^[a-z]*$'")
                        contents = stdout.read().decode().strip()
                        if not contents:
                            result = f"Mount point {mount_point} is empty on {host}"
                        else:
                            result = f"Mount point {mount_point} has files or subdirectories on {host}"
                else:
                    result = f"Mount point {mount_point} is empty on {host}"
            else:
                result = f"Mount point {mount_point} does not exist on {host}"
            ssh.close()
    except Exception as e:
        result = f"Error occurred while checking server {host}: {str(e)}"
    return result

def main():
    returnvalue = {}
    fields = {
        "hostname": {"required": True, "type": "list"},
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},  # This is key file path
        "mount_point": {"required": True, "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)
    try:
        output = check_mount_and_dirs(
            module.params["hostname"],
            module.params["username"],
            module.params["password"],  # path to private key file
            module.params["mount_point"]
        )
        returnvalue["status"] = output
        module.exit_json(**returnvalue)
    except Exception as err:
        returnvalue["status"] = f"Exception occurred: {str(err)}"
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
