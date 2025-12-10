from ansible.module_utils.basic import AnsibleModule
import pandas as pd
pd.set_option('display.expand_frame_repr', False)

DOCUMENTATION = r'''
---
module: fetch_app_owner

description: This module queries the RTU to get app owner of the target host.

version_added: "1.0.0"

options:
    host:
        description: Server on which application validation is to be performed.
        required: true
        type: str
    cmdb_rtu:
        description: CMDB RTU URL
        required: true
        type: str
'''

EXAMPLES = r'''
- name: "Fetch app owner group from CMDB RTU"
  fetch_app_owner:
    host: "{{ inventory_hostname }}"
    cmdb_rtu: "{{CMDB_URL}}"
  register: app_owner_group
  delegate_to: localhost
'''

def get_app_owner(host, cmdb_rtu):
    import pandas as pd
    url = "https://" + cmdb_rtu + "/rtu/?serverName=" + host
    try:
        data_frame = pd.read_json(url)

        # Check if the column exists and is not empty
        if 'rtuApplicationOwnership' in data_frame.columns and not data_frame['rtuApplicationOwnership'].empty:
            app_owner = data_frame['rtuApplicationOwnership'].iloc[0]
            if pd.isna(app_owner) or app_owner == "":
                return "Exception: No Application Owner found"
            else:
                return app_owner
        else:
            return "Exception: No Application Owner column found or it's empty"

    except Exception as err:
        return "Exception: " + str(err)
    
def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"str"},
         "cmdb_rtu":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        app_owner = get_app_owner(module.params["host"],module.params["cmdb_rtu"])
        returnvalue["status"] = app_owner
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "Exception occurred while filtering app owner groups.Kindly check. " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
