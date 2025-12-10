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

def rearrange_data(swt_arista):
    input_data = {
        "arista_out_formatted": swt_arista
    }

    data_lines = input_data["arista_out_formatted"].split("\n")

    output = ""
    grouped_data = {}

    for line in data_lines:
        if line.startswith("muc-az"):
            current_group = line
            if current_group not in grouped_data:
                grouped_data[current_group] = []
        elif line.startswith(" - ") and current_group:
            grouped_data[current_group].append(line.strip())

    for group, data in grouped_data.items():
        output += group + "\n "
        output += "\n ".join(data) + "\n"

    output_data = {
        output
    }

    return output_data


# swt_arista = "muc-az2-cl-1104l:\n - Ethernet7/1 : bhg40012\n - Po1071 : bhg40012\nmuc-az2-cl-1104r:\n - Ethernet7/1 : bhg40012\n - Po1071 : bhg40012\n\nmuc-az2-cl-1104l:\n - Ethernet7/3 : bhp40159\n - Po1073 : bhp40159\nmuc-az2-cl-1104r:\n - Ethernet7/3 : bhp40159\n - Po1073 : bhp40159"

# output = rearrange_data(swt_arista)
# print(output)


def main():
    returnValue = {}
    fields = {
        "swt_arista": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)

    try:
        res = rearrange_data(module.params["swt_arista"])
        returnValue["output_data"] = res
        module.exit_json(**returnValue)

    except Exception as err:
        returnvalue["output_data"] = "[ERROR]" + str(err)
        module.exit_json(**returnvalue) 

if __name__ == '__main__':
    main()
