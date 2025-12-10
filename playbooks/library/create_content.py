#import warnings
import json
from ansible.module_utils.basic import AnsibleModule
#warnings.simplefilter(action='ignore', category=FutureWarning)


def file_content(filepath,cr,ci,requester_name,requester_group,retention_days,ritm_number,pillar,mit_ticket):
    host = ""
    for x in ci:
        host += str(" - "+"hosts:"+" "+"'"+x+"'"+"\r\n")
    payload = "associated_cis:\r\n"+host+"cr: "+cr+"\r\ngraceperiod_flag: 'False'"+"\r\nretention_days: "+retention_days+"\r\nrequester_name: "+requester_name+"\r\nrequester_group: "+requester_group+"\r\nritm_number: "+ritm_number+"\r\npillar: "+pillar+"\r\nmit_ticket: "+mit_ticket+""
    with open(filepath, 'w') as f:
        json.dump(payload, f)
    return "Success"

def main():
    returnvalue = {}
    fields = {
        "filepath":{"required":True, "type":"str"},
        "cr":{"required":True, "type":"str"},
        "ci":{"required":True, "type":"list"},
        "requester_name":{"required":True, "type":"str"},
        "requester_group":{"required":True, "type":"str"},
        "retention_days":{"required":True, "type":"str"},
        "ritm_number":{"required":True, "type":"str"},
        "pillar":{"required":False, "type":"str"},
        "mit_ticket":{"required":False, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    if module.params['pillar'] is None or module.params['pillar'] == '':
        module.params['pillar'] = 'F'
    if module.params['mit_ticket'] is None or module.params['mit_ticket'] == '':
        module.params['mit_ticket'] = 'F'
    try:
        status = file_content(module.params["filepath"],
                            module.params["cr"],
                            module.params["ci"],
                            module.params["requester_name"],
                            module.params['requester_group'],
                            module.params['retention_days'],
                            module.params['ritm_number'],
                            module.params['pillar'],
                            module.params['mit_ticket'])
        returnvalue["status"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Error"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
