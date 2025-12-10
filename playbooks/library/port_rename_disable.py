from ansible.module_utils.basic import *
import paramiko
import time
import re

DOCUMENTATION = r'''
---
module: port_rename_disable

description: This module is used to rename and disable the ports which is associated to the host. 

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
	ip_addr:
        description: IP address of the switch which is associated to the host.
        required: true
        type: str
	port_name:
        description: Ports which is associated to the host.
        required: true
        type: str
		  
author:
    - Dhivya Radhakrishnan (@pdradhak)
'''

EXAMPLES = r'''
	- name: "Testing Port Rename and Disable module"
	  port_rename_disable:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		ip_addr: "{{ ip_addr }}"
		port_name: "{{ item }}"
	  with_items: "{{ ports }}"
	  delegate_to: localhost
	  register: port_rename_disable_output
	  
'''

def rename_disable_port(username,password,ip_addr,port_name):
    try:
        ipaddr=ip_addr
        portname= port_name  
        rename_cmd = "portname -i"
        disable_cmd = "portcfgpersistentdisable -i"

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ipaddr, username=username, password=password, port=22)
        time.sleep(3)
        stdin,stdout,stderr = ssh_client.exec_command(rename_cmd+" "+portname+" "+"-n"+" Unassigned")
        time.sleep(5)
        output = stdout.read().decode().strip()
        if len(output) == 0 or re.search('portName no change', output):
            stdin,stdout,stderr = ssh_client.exec_command(disable_cmd+" "+portname)
            time.sleep(5)
            disable = stdout.read().decode().strip()
            if len(disable) == 0 or re.search('Same Configuration for port', disable):
                value = "Port Renamed and Disabled Successfully"
            else:
                value = "Port Renamed but not Disabled"
        else:
            value = "Rename and Disable of Port failed"
        ssh_client.close()
        return value

    except Exception as e:
        ssh_client.close()
        return str(e)

def main():
    returnValue = dict()
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "ip_addr":{"required":True,"type":"str"},
                "port_name":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        username = module.params["username"]
        password = module.params["password"]
        ip_addr = module.params["ip_addr"]
        port_name = module.params["port_name"]
        port_rename_disable  = rename_disable_port(username,password,ip_addr,port_name)
        returnValue["port_output"] = port_rename_disable       
        module.exit_json(** returnValue)                  
        
    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e)
        module.fail_json(**returnValue)            

if __name__ == '__main__':
    main() 