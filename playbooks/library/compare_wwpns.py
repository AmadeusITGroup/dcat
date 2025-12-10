from ansible.module_utils.basic import *

DOCUMENTATION='''
    This module is used to compare the wwpns from the host with the svc wwpns to process the storage controller cleanup.
'''

def run_module():
    returnValue = dict()
    try:
        fields = {
                "wwpns_fromhost":{"required":True,"type":"list"},
                "wwpns_fromsvc":{"required":True,"type":"list"},
        }
        module = AnsibleModule(argument_spec = fields)

        wwpnshost = module.params["wwpns_fromhost"]
        wwpnssvc = module.params["wwpns_fromsvc"]
        wwpns_host= [x.upper() for x in wwpnshost]
        wwpns_svc= [y.upper() for y in wwpnssvc]
        compare = []
        for i in wwpns_svc:
            if i in wwpns_host:
                compare.append("true")
        if "true" in compare:
            returnValue["data"] =  "matched"
            module.exit_json(**returnValue)
        else:
            returnValue["data"] = "Not matched"
            module.exit_json(**returnValue)

    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e)
        module.fail_json(**returnValue)        

if __name__=='__main__':
    run_module()
