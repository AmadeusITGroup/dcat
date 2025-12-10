from ansible.module_utils.basic import *

DOCUMENTATION = r'''
---
module: switches_check

description: This module is used to check the result generated from the san_process_check custom Ansible module so as to confirm the
the SAN process.

version_added: "1.0.0"

options:
    ip_addr:
        description: IP address of the switch which is associated to the host.
        required: true
        type: str
    hostname:
        description: Server on which SAN cleanup to be performed.
        required: true
        type: str
    check_switches:
        description: san_process_check module output to check.
        required: true
        type: list
		  
author:
    - Dhivya Radhakrishnan (@pdradhak)
'''

EXAMPLES = r'''
	- name: "Testing Switches_Deletion_Check Module"
      switches_check:
        ipaddr: "{{ ip_addr }}"
        hostname: "{{ inventory_hostname }}"
        check_switches: "{{ san_process_info }}"
      register: switches_final_output

'''

def main():
    try:
        returnValue = dict()
        fields = { 
            "ipaddr":{"required":True,"type":"str"},
            "hostname":{"required":True,"type":"str"},    
            "check_switches":{"required":True, "type":"list"},
    }
        module = AnsibleModule(argument_spec = fields)  
        check = []
        for i in module.params["check_switches"]:
            if "success" in i["a_check"]:
                check.append("True")
            elif "fail" in i["a_check"]:
                check.append("False")

        if "False" in check:
            final_check = "san_cleanup_failed for the switch"
            result = "Fail"
        else:
            final_check = "san_cleanup_completed for the switch" 
            result = "Success"
        
        returnValue["switch_san_output"] = module.params["hostname"] + " - " +final_check+" "+ module.params["ipaddr"]  
        returnValue["result"] = result             
        module.exit_json(** returnValue)                     
    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e) 
        module.fail_json(**returnValue)            

if __name__ == '__main__':
    main() 
