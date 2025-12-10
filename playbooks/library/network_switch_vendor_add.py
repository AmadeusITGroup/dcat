from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: backup_removal_linux

description: Removing backup packages "TIVsm-BA" and "TIVsm-API"

version_added: "1.0.0"

options:
    hostname:
        description: list of host for package removal.
        required: true
        type: str
    
author:
    - Thineshkumar R (@thr)
'''

EXAMPLES = r'''
    - name: "Custom module backup software removal"
      backup_removal_linux:
        hostname: "{{ inventory_hostname }}"
        username: "{{ username }}"
        key_filename: "{{ key_filename }}"
      register: backup_package  
'''
RETURN = r'''
status:
    description: Returning the status by length of the list index.
    type: len 
    returned: always

'''
def vend(switch_port,vendor_info):

    output = {}

    for switch in vendor_info:
        switch_parts = switch.split(': ')
        switch_id = switch_parts[0]
        switch_type = switch_parts[1]
        
        if switch_id in switch_port:
            for entry in switch_port[switch_id]:
                entry.append(switch_type)
            output[switch_id] = switch_port[switch_id]
    return output
        
            
def main():
    returnValue = {}
    fields = {     
        "switch_port":{"required":True, "type":"str"},
        "vendor_info":{"required":True, "type":"list"}             
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        output = vend(module.params["switch_port"],module.params["vendor_info"])
                    
        returnValue["output"] = output                         
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnValue["error"] = str(err)
        module.exit_json(**returnValue)              

if __name__ == '__main__':
    main()
