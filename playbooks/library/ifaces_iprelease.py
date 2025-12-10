"""
IP release Custom Module  - Infoblox
"""
from ansible.module_utils.basic import AnsibleModule
import requests

def ifaces_release(host,ipaddress,ipam,username,password,view):
    url_link = "https://"+ipam+"/wapi/v2.1/ipv4address?ip_address="+ipaddress+"&network_view="+view
    response = requests.get(url=url_link, verify=False, auth=(username, password))
    if response.json()[0]['status'] == 'UNUSED':
        #name=response.json()[0]['names'][0]
        result="[INFO], IP reservation already UNUSED for interface IP: "+ipaddress
    else:
        ip_object=response.json()[0]['_ref']
        url="https://"+ipam+"/wapi/v2.1/"+ip_object
        name=response.json()[0]['names'][0]
        response = requests.delete(url,verify=False,auth=(username, password))
        if response.status_code == 200:
           result="[INFO],IP released and status set to UNUSED for interface IP: "+ipaddress+" - name: "+name
        else:
           result="[ERROR],IP release failed with error :"+response.text+"\n"+ip_object
    return result

def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"str"},
         "ipaddress":{"required":True, "type":"str"},
         "ipam":{"required":True, "type":"str"},
         "username":{"required":True, "type":"str","no_log":True},
         "password":{"required":True, "type":"str","no_log":True},
         "view":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        status=ifaces_release(module.params["host"],module.params["ipaddress"],
                          module.params["ipam"],module.params["username"],
                          module.params["password"],module.params["view"])
        returnvalue["Status"] = status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = "[Error]" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()