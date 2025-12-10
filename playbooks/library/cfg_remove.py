from ansible.module_utils.basic import *
import sys 
from pyfos import pyfos_auth
from pyfos import pyfos_util
from pyfos.utils import brcd_util
from pyfos.utils import brcd_zone_util
import pyfos.pyfos_brocade_zone as pyfos_zone
import pyfos.utils.zoning.zoning_cfg_save as cfgsave
import pyfos.utils.zoning.zoning_cfg_abort as cfgabort

DOCUMENTATION = r'''
---
module: cfg_remove

description: This module is used to remove existing zones from existing cfg(s).

version_added: "1.0.0"

options:
    username:
        description: Username of service account used to interact with switch.
        required: true
        type: str
    password:
        description: Password of service account used to interact with switch.
        required: true
        type: str
	ip_addr:
        description: IP address of the switch which is associated to the host.
        required: true
        type: str
	cfg-name:
        description: Fabric name of the switch which is associated to the host.
        required: true
        type: str
	zone-name:
        description: zone names in the switch which is associated to the host.
        required: true
        type: str
		  
'''

EXAMPLES = r'''
	- name: "Testing cfg_remove module"
	  cfg_remove:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		ip_addr: "{{ ip_addr }}"
		cfg-name: "{{ fabric }}"
		zone-name: "{{ item }}"
	  with_items: "{{ zone_names }}"
      delegate_to: localhost 
	  register: cfg_remove_output

'''

def usage():
    print("  Script specific options:")
    print("")
    print("    --name=NAME                  name of cfg")
    print("    --members=MEMBERS            ; separated list of cfg members")
    print("                                 multiple members enclosed by \"\"")
    print("")


def cfgremove(session, cfgs):
    """Remove from existing cfg(s) specified member(s)
    Example usage of the method::
        cfgs = [
                    {
                        "cfg-name": name,
                        "member-zone": {"zone-name": members}
                    }
                  ]
        result = cfgremove(session, cfgs)
    :param session: session returned by login
    :param cfgs: an array of cfg and members
    :rtype: dictionary of return status matching rest response
    *use cases*
        1. remove members from existing cfg
    """

    new_defined = pyfos_zone.defined_configuration()
    new_defined.set_cfg(cfgs)
    result = new_defined.delete(session)
    return result
    
def __cfgremove(session, name, members):
    cfgs = [
            {"cfg-name": name, "member-zone": {"zone-name": members}}
           ]
    return cfgremove(session, cfgs)

def zone_name_members_func(session, inputs, usage, func):
    # comment zone helper to execute & commit
    # name, and member based operations
    if "name" not in inputs:
        print("*** missing input: name")
        pyfos_auth.logout(session)
        brcd_util.full_usage(usage)
        sys.exit()
    name = inputs["name"]

    if "members" not in inputs:
        print("*** missing input: members")
        pyfos_auth.logout(session)
        brcd_util.full_usage(usage)
        sys.exit()
    members = inputs["members"]

    current_effective = pyfos_zone.effective_configuration.get(session)
    value = []
    results = func(session, name, members)
    
    if results["http-resp-code"] == 204:
        value.append("cfg_remove_success")
    else:
        value.append("cfg_remove_fail")
    
    if pyfos_util.is_failed_resp(results):
        result = cfgabort.cfgabort(session)
        if result["http-resp-code"] == 204:
            value.append("cfg_abort_success")
        else:
            value.append("cfg_abort_fail")
    else:
        result = cfgsave.cfgsave(session, current_effective.peek_checksum())
        if pyfos_util.is_failed_resp(result):
            result = cfgabort.cfgabort(session)
            value.append("cfg_save_fail")
        elif result["http-resp-code"] == 204:
            value.append("cfg_save_success")
    
    if value[0] == "cfg_remove_success" and value[1] == "cfg_save_success":
        final_result = "cfg_remove successfully"
    else:
        final_result = "cfg_remove failed"
    
    return final_result

def run_module():
    returnValue = dict()
    try:
        fields = {
            "username":{"required":True, "type":"str"},
            "password":{"required":True, "type":"str", "no_log":True},
            "ip_addr":{"required":True, "type":"str"},
            "cfg-name":{"required":True, "type":"str"},
            "zone-name":{"required":True, "type":"str"},
        }
        module = AnsibleModule(argument_spec = fields)
        inputs = {
            "secured":"self",
            "verbose":0,
            "utilusage":"",
            "ipaddr":module.params["ip_addr"],
            "login":module.params["username"],
            "password":module.params["password"],
            "name":module.params["cfg-name"],
            "members":module.params["zone-name"],
            "vfid":-1,
        } 
        session = pyfos_auth.login(inputs["login"], inputs["password"],
                               inputs["ipaddr"], inputs["secured"],
                               verbose=inputs["verbose"])
                               
        if pyfos_auth.is_failed_login(session):
            raise Exception("login failed.")
        
        brcd_util.exit_register(session)
        vfid = None
        if 'vfid' in inputs.keys():
            vfid = inputs["vfid"]
        if vfid is not None:
            pyfos_auth.vfid_set(session,vfid)

        cfg_remove_output = zone_name_members_func(session, inputs, usage, __cfgremove)
        pyfos_auth.logout(session)
        returnValue["cfg_remove_data"] = cfg_remove_output
        module.exit_json(**returnValue)
        
    except Exception as e:
        returnValue["msg"] = "ERROR: "+str(e)
        pyfos_auth.logout(session)
        module.fail_json(**returnValue)

if __name__=='__main__':
    run_module()