import requests
from io import StringIO
from ansible.module_utils.basic import AnsibleModule


def get_data(username,password,win_target,tr):
    session = requests.Session()
    url="https://"+win_target+"/aproach-api/v1.0/taskrecords/"+tr
    session.auth = (username, password)
    response = session.get(url)
    #if response == 200:
    data = response.json()
    output = data['normalFields']['Status']
    return output

     
def main():
    returnvalue = {}
    fields = {
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
        "win_target":{"required":True, "type":"str"},
        "tr": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        result = get_data(module.params["username"],
                            module.params["password"],module.params["win_target"],
                            module.params["tr"])
        returnvalue["status"] = result
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
