import winrm
from ansible.module_utils.basic import *

def fetch_info_host_windows(hostname, username, password):
    try:
        session = winrm.Session(hostname, auth=(username, password),transport='ntlm')
        result = session.run_cmd('net localgroup Administrators "MUCMSPDOM\svc-deco-app-windows" /add')
        if result.status_code == 0 or 'already' in str(result.std_err):
            winhost = "successfully added User svc-deco-app-windows "
        else:
            winhost = "ERROR: useradd failed"
    except Exception as e:
        winhost = "ERROR:"+ str(e)
    return winhost 

def run_module():
   returnvalue = {}
   fields = {
      "hostname":{"required":True, "type":"str"},
      "username":{"required":True, "type":"str"},
      "password":{"required":True, "type":"str"}
   }
   module = AnsibleModule(argument_spec = fields)
   try:
      window_hostname_status = fetch_info_host_windows(module.params["hostname"],module.params["username"],module.params["password"])
      returnvalue["window_host_result"] = window_hostname_status
      module.exit_json(**returnvalue)
   except Exception as err: 
      returnvalue["window_host_result"] = "[ERROR]" + str(err)
      module.exit_json(**returnvalue)
      
if __name__ == '__main__':
   run_module()