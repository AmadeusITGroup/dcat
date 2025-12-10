import yaml
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

    # Parse switch_port as YAML
    data = yaml.load(switch_port, Loader=yaml.FullLoader)

    # Create final_out
    final_out = {"network_info": {}}
    for item in vendor_info:
        key, value = item.split(": ", 1)
        key = key.strip()
        value = value.strip()
        if value not in final_out["network_info"]:
            final_out["network_info"][value] = {}
        final_out["network_info"][value][key] = data.get(key, [])

    # Convert final_out to YAML
    final = yaml.dump(final_out, default_flow_style=False)
    #print(final)
    return final
    
            

#vend("mucrtp383:\n - Ethernet12/45 : no7dp5i1\n - Ethernet12/46 : no7dp5i1\nmucrtp381:\n - Ethernet12/45 : no7dp5i1\n - Ethernet12/46 : no7dp5i1\nmucrtp869:\n - Ethernet1/30 : no7dp5i1\nmucrtp871:\n - Ethernet1/30 : no7dp5i1\n",["mucrtp381: cisco","mucrtp383: cisco","mucrtp869: arista","mucrtp871: cisco"])    

def main():
    returnValue = {}
    fields = {     
        "switch_port":{"required":True, "type":"str"},
        "vendor_info":{"required":True, "type":"list"}             
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        final = vend(module.params["switch_port"],module.params["vendor_info"])
                    
        #returnValue["final"] = final             
        module.exit_json(changed=False, final=final)                  
        
    except Exception as err:
        #returnValue["final"] = "[ERROR]" + str(err)
        module.fail_json(changed=False, final="[ERROR]" + str(err))             

if __name__ == '__main__':
    main()
