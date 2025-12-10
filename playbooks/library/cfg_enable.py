from ansible.module_utils.basic import *
import sys
from pyfos import pyfos_auth
import pyfos.pyfos_brocade_zone as pyfos_zone
from pyfos import pyfos_util
from pyfos.utils import brcd_util

DOCUMENTATION = r'''
---
module: cfg_enable

description: This module is used to enable Zone DB enforcement with cfg.

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
		  
'''

EXAMPLES = r'''
	- name: "Testing cfg_enable module"
	  cfg_enable:
		username: "{{ creds.username }}"
		password: "{{ creds.password }}"
		ip_addr: "{{ ip_addr }}"
		cfg-name: "{{ fabric }}"
      delegate_to: localhost 
	  register: cfg_enable_output
	  
'''

def usage():
    print("  Script specific options:")
    print("")
    print("    --name=NAME                  name of cfg")
    print("")


def cfgenable(session, cfgname, checksum):
    """Start enforcing Zone DB with cfg specified
    Example usage of the method::
        result = cfgenable(session, cfgname, checksum)
    :param session: session returned by login
    :param cfgname: name of the cfg to be enabled
    :param checksum: database checksum from effective configuration
    :rtype: dictionary of return status matching rest response
    *use cases*
        1. enable cfg
    """

    new_effective = pyfos_zone.effective_configuration()
    new_effective.set_cfg_name(cfgname)
    new_effective.set_checksum(checksum)
    result = new_effective.patch(session)
    return result
    
def run_module():
    returnValue = dict()
    try:
        fields = {
            "username":{"required":True, "type":"str"},
            "password":{"required":True, "type":"str", "no_log":True},
            "ip_addr":{"required":True, "type":"str"},
            "cfg-name":{"required":True, "type":"str"},
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
        
        if "name" not in inputs:
            pyfos_auth.logout(session)
            raise Exception("login failed.")
            sys.exit()
        name = inputs["name"]

        current_effective = pyfos_zone.effective_configuration.get(session)
        cfg_enable_output = cfgenable(session, name, current_effective.peek_checksum())
        pyfos_auth.logout(session)
        returnValue["cfg_enable_data"] = cfg_enable_output
        module.exit_json(**returnValue)
    except Exception as e:
        returnValue["msg"] = "ERROR: "+str(e)
        pyfos_auth.logout(session)
        module.fail_json(**returnValue)

if __name__=='__main__':
    run_module()

