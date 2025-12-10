from ansible.module_utils.basic import *
import paramiko
import time


DOCUMENTATION = r'''
---
module: fetch_zone_names

description: This module fetches the zones along with the wwpns/aliases of the switch which is associated with the host.

version_added: "1.0.0"

options:
    username:
        description: Username of service account used to interact with switch.
        required: true
        type: str
    password:
        description: Password of service account used to interact with switch.
        required: true
        type: str
	hostname:
        description: Server on which SAN cleanup to be performed.
        required: true
        type: str
	ip_addr:
        description: IP address of the switch which is associated to the host.
        required: true
        type: str
		  
author:
    - Dhivya Radhakrishnan (@pdradhak)
'''

EXAMPLES = r'''
	- name: "Test custom module for fetching zone names."
	  fetch_zone_names:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		hostname: "{{ inventory_hostname }}"
		ipaddr: "{{ ip_addr }}" 
	  register: aliases_wwpn_names

'''
def zones(username,password,ipaddr,hostname):
    finallist = []
    try:
        lists = []
        ipaddress=ipaddr
        implementation = "zoneshow"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ipaddress, username=username, password=password, port=22)
        time.sleep(5)
        stdin,stdout,stderr = ssh_client.exec_command(implementation+" "+"*"+hostname+"*")
        output = stdout.read().decode().strip()
        time.sleep(5)
        ssh_client.close()
        
        for line in output.splitlines():
            values = line.replace("\t", "")
            lists.append(values)
        
        finallist = [x.strip(' ') for x in lists]
        return finallist

    except Exception as e:
        ssh_client.close()
        return finallist

def main():
    returnValue = dict()
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "hostname":{"required":True,"type":"str"},
                "ipaddr":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        zones_info = zones(module.params["username"], module.params["password"], module.params["ipaddr"], module.params["hostname"])
        if len(zones_info ) == 0:
            returnValue["zone_names"] = "Command Timed Out"
            returnValue["zone_names_info"] = "zone_names_info_fail"
            module.exit_json(** returnValue)
        elif "does not exist." in zones_info[0]:
            returnValue["zone_names"] = "No aliases found in the switch"
            returnValue["zone_names_info"] = "zone_names_info_fail"
            module.exit_json(** returnValue)
        else:
            returnValue["zone_names"] = zones_info   
            returnValue["zone_names_info"] = "zone_names_info_success" 
            module.exit_json(** returnValue)       
    
    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e)
        module.fail_json(**returnValue)            

if __name__ == '__main__':
    main() 

