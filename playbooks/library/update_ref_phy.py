'''
 State File updation custom module
'''
import time
from io import StringIO
import warnings
import pandas as pd
from ansible.module_utils.basic import AnsibleModule
import requests
pd.options.mode.chained_assignment = None
warnings.simplefilter(action='ignore', category=FutureWarning)


DOCUMENTATION = r'''
---
module: Update module results to reference point to acheive idempotency logic

description: Update module results to reference point to acheive idempotency logic.

version_added: "1.0.0"

options:
    hostname:
        description: Hostname of the DECO server.
        required: true
        type: str

author:
    - Prashanth k (@pk)
'''

EXAMPLES = r'''
- name: check OBE application status - LINUX
          update_ref:
            hostname: "{{hostname}}"
          register: update_status
          delegate_to: localhost
'''

def write_data(hostname,artifacts_user,artifacts_password,state_file_url,lookup_file_phy):
    session = requests.Session()
    url="https://"+state_file_url+"decoautomation-generic-dev-managedser/"+lookup_file_phy
    session.auth = (artifacts_user, artifacts_password)
    response = session.get(url)
    data = response.text
    dataframe = pd.read_csv(StringIO(data))
    if dataframe['hostname'].str.contains(hostname).any():
        #print("already Exists and grepping existing value")
        loc = dataframe.loc[dataframe['hostname'] == hostname]
        idempotent_obj = {}
        cmdb_dup_check= loc['cmdb_dup_check'].item()
        fqdn_info= loc['fqdn_info'].item()
        info = loc['info'].item()
        poweron = loc['poweron'].item()
        cmdb_fetch_bgp = loc['cmdb_fetch_bgp'].item()
        san_info_fetch = loc['san_info_fetch'].item()
        cmdb_fetch_agp = loc['cmdb_fetch_agp'].item()
        backup = loc['backup'].item()
        network = loc['network'].item()
        dns = loc['dns'].item()
        ilo = loc['ilo'].item()
        shutdown = loc['shutdown'].item()
        shutdown_bgp = loc['shutdown_bgp'].item()
        san_cleanup = loc['san_cleanup'].item()
        cmdb_update = loc['cmdb_update'].item()
        serial = loc['serial'].item()
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['info'] = info
        idempotent_obj['cmdb_fetch_bgp'] = cmdb_fetch_bgp
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['cmdb_fetch_agp'] = cmdb_fetch_agp
        idempotent_obj['backup'] = backup
        idempotent_obj['network'] = network
        idempotent_obj['dns'] = dns
        idempotent_obj['ilo'] = ilo
        idempotent_obj['shutdown'] = shutdown
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['poweron'] = poweron
        idempotent_obj['serial'] = serial
        idempotent_obj['shutdown_bgp'] = shutdown_bgp
    else:
        new_entry = {'hostname':hostname,'cmdb_dup_check':'F','fqdn_info':'F','info':'F',
                     'cmdb_fetch_bgp':'F','san_info_fetch':'F','cmdb_fetch_agp':'F',
                     'backup':'F','network':'F','poweron':'F',
                     'dns':'F',
                     'ilo':'F','shutdown':'F',
                     'san_cleanup':'F','cmdb_update':'F','serial':'F','shutdown_bgp':'F'}
        dataframe = dataframe.append(new_entry, ignore_index=True)
        time.sleep(5)
        auth=(artifacts_user,artifacts_password)
        response = requests.put(url, auth=auth, data=dataframe.to_csv(index=False))
        idempotent_obj = {}
        hostname=hostname
        cmdb_dup_check='F'
        fqdn_info='F'
        info='F'
        cmdb_fetch_bgp='F'
        san_info_fetch='F'
        cmdb_fetch_agp='F'
        backup='F'
        network='F'
        dns='F'
        ilo='F'
        shutdown='F'
        san_cleanup='F'
        cmdb_update='F'
        poweron='F'
        serial='F'
        shutdown_bgp='F'
        idempotent_obj['cmdb_dup_check'] = cmdb_dup_check
        idempotent_obj['fqdn_info'] = fqdn_info
        idempotent_obj['info'] = info
        idempotent_obj['cmdb_fetch_bgp'] = cmdb_fetch_bgp
        idempotent_obj['san_info_fetch'] = san_info_fetch
        idempotent_obj['cmdb_fetch_agp'] = cmdb_fetch_agp
        idempotent_obj['backup'] = backup
        idempotent_obj['network'] = network
        idempotent_obj['dns'] = dns
        idempotent_obj['ilo'] = ilo
        idempotent_obj['shutdown'] = shutdown
        idempotent_obj['san_cleanup'] = san_cleanup
        idempotent_obj['cmdb_update'] = cmdb_update
        idempotent_obj['poweron'] = poweron
        idempotent_obj['serial'] = serial
        idempotent_obj['shutdown_bgp'] = shutdown_bgp
    return idempotent_obj
    

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "artifacts_user":{"required":True, "type":"str","no_log":True},
        "artifacts_password":{"required":True, "type":"str","no_log":True},
        "state_file_url":{"required":True, "type":"str"},
        "lookup_file_phy": {"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status = write_data(module.params["hostname"],module.params["artifacts_user"],
                            module.params["artifacts_password"],module.params["state_file_url"],
                            module.params["lookup_file_phy"])
        returnvalue["module_update"] = status
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["module_update"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()