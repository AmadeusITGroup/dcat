from ansible.module_utils.basic import *
import re
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

def net(swt_port):
    res = []

    for i in range(0, len(swt_port), 3):
        switch = swt_port[i][0]
        ports = swt_port[i+1].split(',')
        server = swt_port[i+2].split(',')
        
        for port in ports:
            res.append({"port": port, "sw": switch, "server": server})
    return res



def main():
    returnValue = dict()
    fields = {
        "swt_port": {"required": True, "type": "list"}
    }
    module = AnsibleModule(argument_spec=fields)

    try:
        res = net(module.params["swt_port"])
        returnValue["res"] = res
        module.exit_json(**returnValue)

    except Exception as err:
        returnvalue["res"] = "[ERROR]" + str(err)
        module.exit_json(**returnvalue) 


if __name__ == '__main__':
    main()