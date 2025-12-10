from ansible.module_utils.basic import AnsibleModule
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
module: zone_delete

description: This module is used to delete existing Zone(s) which is removed from configuration.

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
	zone-name:
        description: zones which is associated to the host.
        required: true
        type: str
		  
author:
    - Dhivya Radhakrishnan (@pdradhak)
'''

EXAMPLES = r'''
	- name: "Testing zone_delete module"
	  zone_delete:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		ip_addr: "{{ ip_addr }}"
		zone-name: "{{ item }}"
	  with_items: "{{ zone_names }}"
      delegate_to: localhost 
	  register: zone_delete_output
	  
'''

def zonedelete(session, zones):
    """Delete an existing Zone(s)
    Example usage of the method::
        zones = [
                    {
                        "zone-name": name,
                    }
               ]
        result = zonedelete(session, zones)
    :param session: session returned by login
    :param zones: an array of zone and new members
    :rtype: dictionary of return status matching rest response
    *use cases*
        1. Delete an existing Zone(s)
    """

    new_defined = pyfos_zone.defined_configuration()
    new_defined.set_zone(zones)
    result = new_defined.delete(session)
    return result


def __zonedelete(session, name):
    zones = [
                {"zone-name": name}
            ]
    return zonedelete(session, zones)


def usage():
    print("  Script specific options:")
    print("")
    print("    --name=NAME                  name of zone")
    print("")

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
        value.append("zone_delete_success")
    else:
        value.append("zone_delete_fail")

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
    
    if value[0] == "zone_delete_success" and value[1] == "cfg_save_success":
        final_result = "Zone Deleted Successfully"
    else:
        final_result = "Zone Deletion Failed"
    
    return final_result

def run_module():
    returnValue = dict()
    try:
        fields = {
            "username":{"required":True, "type":"str"},
            "password":{"required":True, "type":"str","no_log":True},
            "ip_addr":{"required":True, "type":"str"},
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
            "name":module.params["zone-name"],
            "vfid":-1,
        } 
        session = pyfos_auth.login(inputs["login"], inputs["password"],
                               inputs["ipaddr"], inputs["secured"],
                               verbose=inputs["verbose"])
        zonenames = inputs["name"]
        if pyfos_auth.is_failed_login(session):
            raise Exception("login failed.")
        
        brcd_util.exit_register(session)
        vfid = None
        if 'vfid' in inputs.keys():
            vfid = inputs["vfid"]
        if vfid is not None:
            pyfos_auth.vfid_set(session,vfid)
        
        zone_output = zone_name_func(session, inputs, usage, __zonedelete)
        returnValue["zone_delete_data"] = zone_output
        pyfos_auth.logout(session)
        module.exit_json(**returnValue)
    except Exception as e:
        returnValue["msg"] = "ERROR: "+str(e)
        pyfos_auth.logout(session)
        module.fail_json(**returnValue)

if __name__=='__main__':
    run_module()