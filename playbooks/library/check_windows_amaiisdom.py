from ansible.module_utils.basic import AnsibleModule
import requests
import pandas as pd
import json


def categorize_os(hosts, cmdb_rtu):
    returnvalue = {
        "amaiisdom_windows_machines": [],
        "no_data_machines": []
    }
    for host in hosts:
        url = "https://"+cmdb_rtu+"/rtu/?serverName="+host.lower()
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            data_frame = pd.read_json(response.text)
            if data_frame.empty:
                returnvalue["no_data_machines"].append(host)
            else:
                server_os_name = data_frame.iloc[0]['serverOSName']
                if 'windows' in server_os_name.lower():  #Red Hat Enterprise
                    server_fqdn = data_frame.iloc[0]['serverFQDN']
                    if 'excluded_domains' in server_fqdn:
                        returnvalue["amaiisdom_windows_machines"].append(host)
                    else:
                        pass
                else:
                    pass
        except (json.JSONDecodeError, requests.RequestException):
            returnvalue["no_data_machines"].append(host)
        except Exception:
            returnvalue["no_data_machines"].append(host)
    return returnvalue

def run_module():
    fields = {
         "hosts":{"required":True, "type":"list"},
         "cmdb_rtu":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        osinfo = categorize_os(hosts = module.params["hosts"],cmdb_rtu= module.params["cmdb_rtu"])
        returnvalue["status"] = osinfo
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
