from ansible.module_utils.basic import AnsibleModule
import paramiko
import os
import time
import warnings
import tempfile
from jinja2 import Environment, FileSystemLoader
from paramiko import RSAKey, Ed25519Key, ECDSAKey, DSSKey, SSHException


warnings.filterwarnings("ignore")  # Ignore SSH warnings


def render_template(src, variables):
    """
    Renders a Jinja2 template file with the given variables.
    """
    try:
        template_dir, template_file = os.path.split(src)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)
        return template.render(variables)
    except Exception as e:
        raise Exception(f"Failed to render template '{src}': {str(e)}")


def ssh_connect(hostname, username, key_filename):
    """
    Establish an SSH connection with fallback authentication methods.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    pkey = None
    key_errors = []

    for key_class in [RSAKey, Ed25519Key, ECDSAKey, DSSKey]:
        try:
            pkey = key_class.from_private_key_file(key_filename)
            break
        except SSHException as e:
            key_errors.append(f"{key_class.__name__}: {str(e)}")
        except Exception:
            continue  # Ignore file format errors for key types that clearly don't match

    if not pkey:
        raise Exception(f"Failed to load private key '{key_filename}'. Errors: {key_errors}")


    try:
        # Try connecting with default settings
        ssh.connect(hostname=hostname, username=username, key_filename=key_filename, port=22, timeout=5)
        return ssh
    except Exception as e:
        try:
            # Fallback to SHA1 algorithms
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname, username=username, key_filename=key_filename, port=22, timeout=5, **fallback_to_sha1)
            return ssh
        except Exception as e2:
            raise Exception(f"SSH connection failed for host {hostname} with ERROR: {str(e2)}")


def ssh_copy_file(hostname, username, key_filename, src, dest, variables):
    """
    Copies a file from the local system to a remote server using SSH after rendering it.
    """
    try:
        rendered_content = render_template(src, variables)
        ssh = ssh_connect(hostname, username, key_filename)
        sftp = ssh.open_sftp()

        # Write the rendered content to a temporary file
        # local_temp_file = f"/tmp/{os.path.basename(src)}.rendered"
        # with open(local_temp_file, "w") as f:
        #     f.write(rendered_content)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmpfile:
            tmpfile.write(rendered_content)
            local_temp_file = tmpfile.name

        # Try to remove the file at the destination (to avoid permission denied)
        try:
            sftp.remove(dest)
        except IOError:
            pass  # If the file doesn't exist, ignore

        
        # Copy the rendered file to the destination
        sftp.put(local_temp_file, dest)

        # Clean up the local temporary file
        os.remove(local_temp_file)

        sftp.close()
        ssh.close()
        return {"status": "success", "message": f"Rendered and copied {src} to {dest} on {hostname}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_module():
    """
    Defines the Ansible module and processes the parameters.
    """
    module_args = {
        "hostname": {"type": "str", "required": True},
        "username": {"type": "str", "required": True},
        "key_filename": {"type": "str", "required": True},
        "src": {"type": "str", "required": True},
        "dest": {"type": "str", "required": True},
        "variables": {"type": "dict", "required": False, "default": {}},
    }
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Call the ssh_copy_file function
    result = ssh_copy_file(
        hostname=module.params["hostname"],
        username=module.params["username"],
        key_filename=module.params["key_filename"],
        src=module.params["src"],
        dest=module.params["dest"],
        variables=module.params["variables"],
    )

    # Handle success or failure
    if result["status"] == "success":
        module.exit_json(changed=True, msg=result["message"])
    else:
        module.fail_json(msg=result["message"])


if __name__ == "__main__":
    run_module()
