from ansible.module_utils.basic import AnsibleModule
import paramiko
import time
import warnings
warnings.filterwarnings("ignore")



def fetch_info_host(hostname,username,password):
   output={}
   data_list=[]
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   try:
      ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,timeout=5)
      time.sleep(2)
      stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -s)|grep 'has address'|awk '{print $1}'")
      time.sleep(2)
      output = stdout.readlines()
      ssh.close()
      return output 
   except Exception as e:
      try:
         fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
         ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,**fallback_to_sha1)
         time.sleep(2)
         stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -s)|grep 'has address'|awk '{print $1}'")
         time.sleep(2)
         output = stdout.readlines()
         ssh.close()
         return output
      except Exception as e:
         return "SSH check Failed for host - "+ hostname + " with ERROR --> " + str(e)

def run_module():
   returnvalue = {}
   fields = {
      "hostname":{"required":True, "type":"str"},
      "username":{"required":True, "type":"str"},
      "key_filename":{"required":True, "type":"str"}
   }
   module = AnsibleModule(argument_spec = fields)
   try:
      info_status = fetch_info_host(hostname=module.params["hostname"],
                                    username=module.params["username"],
                                    password=module.params["key_filename"])
      returnvalue["host_result"] = info_status
      module.exit_json(**returnvalue)
   except Exception as err: # pylint: disable=broad-except
      returnvalue["host_result"] = "[ERROR]" + str(err)
      module.exit_json(**returnvalue)
      
if __name__ == '__main__':
   run_module()   
