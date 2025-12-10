from ansible.module_utils.basic import *

DOCUMENTATION='''
    This module filters a list of volumes by whether are to be renamed and generates their new name.
    New name format: DECO_TRNUMBER_oldname
'''

def run_module():
    returnValue = dict()
    try:
        fields = {
                "vols":{"required":True,"type":"list"},
                "TR":{"required":True,"type":"str"},
        }
        module = AnsibleModule(argument_spec = fields)
        rename_list = [] 
        for vol in module.params["vols"]:
            if vol["rename"] == True: # and "DECO" in vol["volname"]:
                oldname = vol["volname"]
                newname = "DECO_"+module.params["TR"]+"_"+vol["volname"]
                volume = {
                    "oldname":oldname,
                    "newname":newname
                }
                rename_list.append(volume)
        returnValue["vols"] = rename_list
        module.exit_json(**returnValue)
    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e)
        module.fail_json(**returnValue)        

if __name__=='__main__':
    run_module()
