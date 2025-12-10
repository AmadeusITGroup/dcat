from ansible.module_utils.basic import AnsibleModule
import paramiko
import time
import warnings
warnings.filterwarnings("ignore")

def fetch_info_host(hostname,username,password):
   result={}
   data_list=[]
   online = []
   offline = []
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
      result['os_name']=data.strip()
   else:
      result['os_name']= 'NA'
   #stdin, stdout, stderr = ssh.exec_command("cat /sys/class/fc_host/host?/port_name")
   stdin, stdout, stderr = ssh.exec_command('systool -c fc_host -v | egrep "port_name | port_state"')
   time.sleep(2)
   output = stdout.readlines()

   for i in range(0, len(output),2):
      port_name = output[i].split('=')[1].strip().strip('"')
      port_state = output[i+1].split('=')[1].strip().strip('"')
      if port_state == "Online":
         online.append(port_name)
      else:
         offline.append(port_name)

   if len(online)!= 1:
      for item in online:
         data = item.replace("\n", "").replace("0x", "")
         data_list.append(data)     
      result['WWPN']=data_list
   elif len(online)== 1 :
      if online[0][0]== "0" and online[0][1]== "x" :
         data = online[0].replace("0x", "")
         data_list.append(data)
         result['WWPN']= data_list
      else:
         result['WWPN']= 'NA'    
   else:
      result['WWPN']= 'NA'
   stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -f)|grep 'has address'|awk '{print $1}'")
   time.sleep(2)
   output = stdout.readlines()
   if output:
      data = ''.join(map(str, output))
      result['fqdn']=data.strip()
   else:
      result['fqdn']= 'NA'
   stdin, stdout, stderr = ssh.exec_command("host -TtA $(hostname -f)|grep 'has address'|awk '{print $4}'")
   time.sleep(2)
   output = stdout.readlines()
   if output:
      data = ''.join(map(str, output))
      result['ip']=data.strip()
   else:
      result['ip']= 'NA'
   ssh.close()
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
