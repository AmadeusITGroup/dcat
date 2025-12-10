from ansible.module_utils.basic import AnsibleModule
import paramiko
import time
import warnings
warnings.filterwarnings("ignore")


def fetch_info_host(hostname,username,password):
   result={}
   data_list=[]
   #commands=[""]
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   try:
      ssh.connect(hostname=hostname,username=username,key_filename=password,port=22)
   except Exception as e:
      try:
         fallback_to_sha1 = {'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
         ssh.connect(hostname=hostname,username=username,key_filename=password,port=22,**fallback_to_sha1)
         time.sleep(2)
      except Exception as e:
         pass
   time.sleep(2)
   stdin, stdout, stderr = ssh.exec_command("uname")
   time.sleep(2)
   output = stdout.readlines()
   if output:
      data = ''.join(map(str, output))
      data.encode("utf-8")
      result['os_name']=data.strip()
   else:
      result['os_name']= 'NA'
   stdin, stdout, stderr = ssh.exec_command("cat /sys/class/fc_host/host?/port_name")
   time.sleep(2)
   output = stdout.readlines()
   if len(output)!= 1:
      for item in output:
         data = item.replace("\n", "").replace("0x", "")
         data_list.append(data)    
      result['WWPN']=data_list
   elif len(output)== 1 :
      if output[0][-1] == "\n" and output[0][0]== "0" and output[0][1]== "x":
         data = output[0].replace("\n", "").replace("0x", "")
         data.encode("utf-8")
         result['WWPN']= data
      else:
         result['WWPN']= 'NA'    
   else:
      result['WWPN']= 'NA'
   stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -s)|grep 'has address'|awk '{print $1}'")
   time.sleep(2)
   output = stdout.readlines()
   if output:
      data = ''.join(map(str, output))
      data.encode("utf-8")
      result['fqdn']=data.strip()
   else:
      result['fqdn']= 'NA'
   stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -s)|grep 'has address'|awk '{print $4}'")
   time.sleep(2)
   output = stdout.readlines()
   if output:
      data = ''.join(map(str, output))
      data.encode("utf-8")
      result['ip']=data.strip()
   else:
      result['ip']= 'NA'
   ssh.close()
   #print(result)
   return result

def run_module():
   returnvalue = {}
   fields = {
      "hostname":{"required":True, "type":"str"},
      "username":{"required":True, "type":"str","no_log":True},
      "password":{"required":True, "type":"str","no_log":True}
   }
   module = AnsibleModule(argument_spec = fields)
   try:
      info_status = fetch_info_host(module.params["hostname"],module.params["username"],module.params["password"])
      returnvalue["host_result"] = info_status
      module.exit_json(**returnvalue)
   except Exception as err: # pylint: disable=broad-except
      returnvalue["host_result"] = "[ERROR]" + str(err)
      module.exit_json(**returnvalue)
      
if __name__ == '__main__':
   run_module()   
