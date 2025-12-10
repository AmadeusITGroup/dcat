from ansible.module_utils.basic import AnsibleModule
import requests
import urllib3
urllib3.disable_warnings()

def del_record(hostname,ipam,username,password,dns_view,record_type):
    if record_type == 'ptr':
        url='https://'+ipam+'/wapi/v2.1/record:'+record_type+'?ptrdname~='+hostname+'&view='+dns_view
    else:
        url='https://'+ipam+'/wapi/v2.1/record:'+record_type+'?name~='+hostname+'&view='+dns_view
    response = requests.get(url, verify=False, auth=(username, password))
    if response.status_code == 200:
        if len(response.json()) == 0:
            result = record_type+" record not available/already removed for host: "+hostname
        else:
            try:
                object_id = response.json()[0]['_ref']
            except Exception as err:   # pylint: disable=broad-except
                result=record_type+" record removal failed for host: "+hostname+ " Error: "+str(err)
            url='https://'+ipam+'/wapi/v2.1/'+object_id
            response = requests.delete(url,verify=False,auth=(username, password))
            if response.status_code == 200:
                result = record_type+" record removed for host: "+hostname
            else:
                result=record_type+" record removal failed for host:"+hostname+" Error:"+response.text
    else:
        result = record_type+" record removal failed for host: "+hostname+ " Error: "+response.text
    return result

def main():
    returnvalue = {}
    fields = {
        "hostname":{"required":True, "type":"str"},
        "ipam":{"required":True, "type":"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True},
        "dns_view":{"required":True, "type":"str"},
        "record_type":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)

    try:
        status = del_record(module.params["hostname"],
                            module.params["ipam"],
                            module.params["username"],
                            module.params["password"],
                            module.params["dns_view"],
                            module.params["record_type"])
        returnvalue["status"] = status
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "Exception occurred during IPAM cleanup, needs attention "+ str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
