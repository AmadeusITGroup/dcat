from ansible.module_utils.basic import AnsibleModule
import pandas as pd
pd.set_option('display.expand_frame_repr', False)

DOCUMENTATION = r'''
---
module: Fetch Application RTU OBE OLTP Application

description: This module Queries the RTU OBE OTLP application URL to form the target app which will be validated 
on the target host.

version_added: "1.0.0"

options:
    host:
        description: Server on which application validation to be performed.
        required: true
        type: str
    obe_app:
        description: OBE OLTP Application Server 
        required: true
        type: str
author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
      - name: "fetch RTUs for OBE OLTP"
          obe_validation:
            host: "{{inventory_hostname}}"
            obe_app: "{{CMDB_URL}}"
          register: obe_application_name
          delegate_to: localhost
'''
def fetch_app(host,obe_app,instance_id):
    url = "https://"+obe_app+"/rtu/?serverIsVirtual=Yes&rtuSubArea=OBE"
    data_frame = pd.read_json(url)
    data=data_frame.loc[data_frame['serverName'] == host]
    if data.empty:
        app_name = "NA"
    else:
        if len(data) == 1:
            short_name = data['rtuSomoShortName'].item()
            component_name = data['rtuComponentShortName'].item()
            component_role = data['rtuComponentRole'].item()
            env = data['rtuEnvironment'].item()
            app_name = short_name+'-'+component_name+'-'+component_role+'-'+env
        else:
            duplicate = data[data["serverCiInstanceId"] == instance_id]
            if len(duplicate) >= 2:
                app_name =  "Duplicate Entries Found , DECO process stopped for host :"+host
            else:
                data.drop(data.loc[data['serverCiInstanceId'] != instance_id].index, inplace=True)
                if len(data) == 0:
                    app_name = "Instance ID didnt match , DECO process stopped for host :"+host
                else:
                    short_name = data['rtuSomoShortName'].item()
                    component_name = data['rtuComponentShortName'].item()
                    component_role = data['rtuComponentRole'].item()
                    env = data['rtuEnvironment'].item()
                    app_name = short_name+'-'+component_name+'-'+component_role+'-'+env
    return app_name

def os_type(host,obe_app):
    url = "https://"+obe_app+"/rtu/?serverIsVirtual=Yes&rtuSubArea=OBE"
    data_frame = pd.read_json(url)
    data=data_frame.loc[data_frame['serverName'] == host]
    data = data.drop_duplicates(subset='serverCiInstanceId', keep="first")
    if data.empty:
        os_info = "NA"
    else:
        if 'SuSE Linux Enterprise' in data['rtuOSProduct'].item():
            os_info = "Linux"
        else:
            os_info = "Windows"
    return os_info

def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"str"},
         "obe_app":{"required":True, "type":"str"},
         "instance_id":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        app_name = fetch_app(module.params["host"],
                             module.params["obe_app"],
                             module.params["instance_id"])
        os_name = os_type(module.params["host"],module.params["obe_app"])
        returnvalue["OS_type"] = os_name
        returnvalue["OBE_application_name"] = app_name
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
