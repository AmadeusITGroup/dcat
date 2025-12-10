from ansible.module_utils.basic import AnsibleModule
import paramiko
import time
import warnings
warnings.filterwarnings("ignore")

# hostname="ob7dx100"
# username="autodecopoc"
# password="UseDynamite!"

def fetch_info_host(hostname,username,password):
   result={}
   data_list=[]
   #commands=[""]
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   try:
        ssh.connect(hostname=hostname,username=username,password=password, port=22)
   except Exception:
        try:
            fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
            ssh.connect(hostname=hostname, username=username, password=password, port=22, **fallback_to_sha1)
        except Exception as e:
            return f"[Exception] Connection failed: {e}"
   time.sleep(2)
   stdin, stdout, stderr = ssh.exec_command("power off")
   output = stdout.readlines()
   return output

def run_module():
   returnvalue = {}
   fields = {
      "hostname":{"required":True, "type":"str"},
      "username":{"required":True, "type":"str"},
      "password":{"required":True, "type":"str"}
   }
   module = AnsibleModule(argument_spec = fields)
   try:
      info_status = fetch_info_host(module.params["hostname"],module.params["username"],module.params["password"])
      returnvalue["Status"] = info_status
      module.exit_json(**returnvalue)
   except Exception as err: # pylint: disable=broad-except
      returnvalue["Status"] = "[ERROR] - Unable to poweron server" + str(err)
      module.exit_json(**returnvalue)
      
if __name__ == '__main__':
   run_module()