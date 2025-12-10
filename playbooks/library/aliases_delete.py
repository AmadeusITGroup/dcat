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
module: aliases_delete

description: This module is used to delete existing alias(es).

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
	alias-name:
        description: Aliases which is associated to the host.
        required: true
        type: str
		  
author:
    - Dhivya Radhakrishnan (@pdradhak)
'''

EXAMPLES = r'''
	- name: "Testing Aliases_Delete Module"
	  aliases_delete:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		ip_addr: "{{ ip_addr }}"
		alias-name: "{{ item }}"
	  with_items: "{{ aliases }}"
      delegate_to: localhost 
	  register: aliases_delete_output
	  
'''
def usage():
    print("  Script specific options:")
    print("")
    print("    --name=NAME                  name of alias")
    print("")


def aliasdelete(session, aliases):
    """Delete alisas(es)
    Example usage of the method::
        aliases = [
                    {
                        "alias-name": name,
                    }
                  ]
        result = aliadelete(session, aliases)
    :param session: session returned by login.
    :param aliases: an array of alias to be deleted.
    :rtype: Dictionary of return status matching rest response
    *Use cases*
        Delete an alias.
    """

    new_defined = pyfos_zone.defined_configuration()
    new_defined.set_alias(aliases)
    result = new_defined.delete(session)
    return result
    
def __aliasdelete(session, name):
    aliases = [
                {"alias-name": name}
              ]
    return aliasdelete(session, aliases)

def zone_name_func(session, inputs, usage, func):
    # comment zone helper to execute & commit
    # name based operations
    if "name" not in inputs:
        print("*** missing input: name")
        pyfos_auth.logout(session)
        brcd_util.full_usage(usage)
        sys.exit()
    name = inputs["name"]

    current_effective = pyfos_zone.effective_configuration.get(session)
    value = []
    results = func(session, name)
    
    if results["http-resp-code"] == 204:
        value.append("alias_delete_success")
    else:
        value.append("alias_delete_fail")
    
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
    
    
    if value[0] == "alias_delete_success" and value[1] == "cfg_save_success":
        final_result = "Alias Deleted Successfully"
    else:
        final_result = "Alias Deletion Failed"
    
    return final_result


def run_module():
    returnValue = dict()
    try:
        fields = {
            "username":{"required":True, "type":"str"},
            "password":{"required":True, "type":"str", "no_log":True},
            "ip_addr":{"required":True, "type":"str"},
            "alias-name":{"required":True, "type":"str"},
        }
        module = AnsibleModule(argument_spec = fields)
        inputs = {
            "secured":"self",
            "verbose":0,
            "utilusage":"",
            "ipaddr":module.params["ip_addr"],
            "login":module.params["username"],
            "password":module.params["password"],
            "name":module.params["alias-name"],
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
        
        alias_output = zone_name_func(session, inputs, usage, __aliasdelete)
        pyfos_auth.logout(session)
        returnValue["aliases_delete_data"] = alias_output
        module.exit_json(**returnValue)
    except Exception as e:
        returnValue["msg"] = "ERROR: "+str(e)
        pyfos_auth.logout(session)
        module.fail_json(**returnValue)

if __name__=='__main__':
    run_module()