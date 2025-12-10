import time
from ansible.module_utils.basic import AnsibleModule
import paramiko
import datetime

def checklin(hostname,username,password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,timeout=5)
            time.sleep(2)
            ssh.close()
            now = datetime.datetime.now()
            return "SSH check completed and server still accessible - TIME: " + str(now)
        except Exception as e:
            try:
                fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
                ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,timeout=5,**fallback_to_sha1)
                time.sleep(2)
                ssh.close()
                now = datetime.datetime.now()
                return "SSH check completed and server still accessible - TIME: " + str(now)
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
        returnvalue["msg"] = "Exception occurred during ssh, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()