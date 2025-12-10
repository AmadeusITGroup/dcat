import json
from ansible.module_utils.basic import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def dcm_content(location_content):
    try:
        Rooms = {}
        if location_content != "":
            all_location_details = location_content.rstrip(",").replace("'", "\"").replace("\\n", "")
            out = all_location_details
            output = json.loads(out)
            Rooms = {}
            # Loop through servers and group by site
            for server_data in output:
                Room = server_data[next(iter(server_data))]['room']
                Rooms.setdefault(Room, []).append(server_data)
            endres = Rooms
        else:
            endres = None
        return endres
    except Exception as e:
        endres="Error: " + str(e)
        return endres

def run_module():
    fields = {
        "location_content":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        dcmdata =  dcm_content(location_content = module.params["location_content"])
        returnvalue["dcm_content"] = dcmdata
        module.exit_json(**returnvalue)
    except Exception as err:
        returnvalue["dcm_content"]="Exception occurred " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()