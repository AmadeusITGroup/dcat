#import warnings
import json
from ansible.module_utils.basic import AnsibleModule
#warnings.simplefilter(action='ignore', category=FutureWarning)

# filepath="/home/ppk1/deco-automation/playbooks/run_data.json"
# cr="27172570"
# cr="vmdecovt002\nvmdecovt003"
# requester_name = "Prashanth"
# requester_group = "DECOIND"
# retention_days="15"

def file_content(filepath,cr,ci,requester_name,requester_group,retention_days,ritm_number):
    # content={
    #     'cr': cr,
    #     'graceperiod_flag': "False",
    #     'requester_name': requester_name,
    #     'requester_group': requester_group,
    #     'retention_days': retention_days,
    #     'ritm_number': ritm_number
    # }
    #graceperiod_flag="False"
    #ci_new = ci.split('\n')
    host = ""
    for x in ci:
        #print(x)
        host += str(" - "+"hosts:"+" "+"'"+x+"'"+"\r\n")
        #print(host)
        #time.sleep(1)    
    payload = "associated_cis:\r\n"+host+"cr: "+cr+"\r\ngraceperiod_flag: 'False'"+"\r\nretention_days: "+retention_days+"\r\nrequester_name: "+requester_name+"\r\nrequester_group: "+requester_group+"\r\nritm_number: "+ritm_number+""
    #print(payload)
    # d=[]
    # for val in ci_new:
    #   d.append("hosts:"+val)
    # content['associated_cis'] = d
    with open(filepath, 'w') as f:
        #json.dump(payload, f, indent=2)
        f.write(payload)
    return "Success"

file_content("run_data.json","12345",['vmdecovt002','vmdecovt003'],"decotst","decotst","20","ritm1234")    

# def main():
#     returnvalue = {}
#     fields = {
#         "filepath":{"required":True, "type":"str"},
#         "cr":{"required":True, "type":"str"},
#         "ci":{"required":True, "type":"str"},
#         "requester_name":{"required":True, "type":"str"},
#         "requester_group":{"required":True, "type":"str"},
#         "retention_days":{"required":True, "type":"str"},
#         "ritm_number":{"required":True, "type":"str"}
#     }
#     module = AnsibleModule(argument_spec = fields)
#     try:
#         status = file_content(module.params["filepath"],
#                             module.params["cr"],
#                             module.params["ci"],
#                             module.params["requester_name"],
#                             module.params['requester_group'],
#                             module.params['retention_days'],
#                             module.params['ritm_number'])
#         returnvalue["status"] = status
#         module.exit_json(**returnvalue)

#     except Exception as err: # pylint: disable=broad-except
#         returnvalue["Error"] = "[Error]" + str(err)
#         module.exit_json(**returnvalue)

# if __name__ == '__main__':
#     main()
