from io import StringIO
import warnings
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
import requests
pd.options.mode.chained_assignment = None
warnings.simplefilter(action='ignore', category=FutureWarning)


def write_data(cr,module_name,result,artifacts_user,
               artifacts_password,state_file_url,lookup_file):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file
    username= artifacts_user
    pwd= artifacts_password
    session.auth = (username, pwd)
    response = session.get(url)
    data = response.text
    data_frame = pd.read_csv(StringIO(data))
    if str(data_frame['cr'].item()) == cr:
        data_frame[module_name] = result
        auth=(username,pwd)
        response = requests.put(url, auth=auth, data=data_frame.to_csv(index=False))
        status = module_name+" : status updated for cr :  " + cr
    else:
        status = module_name+" not found and unable to update for cr : "+ cr
    return status


def main():
    returnvalue = {}
    fields = {
        "cr":{"required":True, "type":"str"},
        "module_name":{"required":True, "type":"str"},
        "status":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str"},
        "artifacts_password":{"required":True, "type":"str"},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["cr"],
                            module.params["module_name"],
                            module.params["status"],
                            module.params["artifacts_user"],
                            module.params["artifacts_password"],
                            module.params["state_file_url"],
                            module.params["lookup_file"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
