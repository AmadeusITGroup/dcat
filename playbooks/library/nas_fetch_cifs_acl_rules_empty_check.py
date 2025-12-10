import time
import re
import paramiko
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: 

description: This module is used to check if ACL is present in a specific volume associated with shares associated to the host. 

version_added: "1.0.0"

options:
    username:
        description: Username of service account used to interact with storage box.
        required: true
        type: str
    password:
        description: Password of service account used to interact with storage box.
        required: true
        type: str
    storage_box:
        description: storage box where the shares for the server is configured.
        required: true
        type: str
    vol_name:
        description: name of the volume.
        required: true
        type: str
          
author:
    - Leethu T L (@pltl)
'''

EXAMPLES = r'''
    - name: "fetch share informaton associated to the host module"
      :
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
        storage_box: "{{ ip_addr }}"
        vol_name: "{{ item }}"
      delegate_to: localhost
      register: 
      
'''
def fetch_cifs_acl(username,password,storage_box,vol_name,v_server):

    vol_acl_cmd = "cifs share show -volume " + vol_name + " -fields acl,volume"
    vol_policy_cmd = "volume show " + vol_name + " -fields policy"

#####login to th ssh and run te acl check command #############
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(storage_box, username=username, password=password, port=22)
    time.sleep(3)
    stdin,stdout,stderr = ssh_client.exec_command(vol_acl_cmd)
    time.sleep(5)
    output = stdout.read().decode().strip()
############################ checking if the volume has acl ###################
    if len(output) == 0 or re.search('There are no entries matching your query', output):
        time.sleep(3)
        stdin,stdout,stderr = ssh_client.exec_command(vol_policy_cmd)
        time.sleep(5)
        output_vol_pol = stdout.read().decode().strip()
############################ checking if the volume has export policy ###################
        if  len(output_vol_pol) == 0 or re.search('There are no entries matching your query', output_vol_pol):
            msg = "NO ACL and No Rule"
            msg_output = "No ACL and rule entries volume check"
        else:
            list_out_vol = list(output_vol_pol.split(" "))
            list_out_vol = [i for i in list_out_vol if i]
            del list_out_vol[0 :12]
            policy_name = list_out_vol[0]
            #print(list_out_vol)
            if  len(list_out_vol) == 1 and list_out_vol[0] == "-" :
                msg = "NO ACL and No Rule"
                msg_output = "No ACL and rule entries from - volume check "
            else: ### volume has export policy name
                export_policy_cmd = "export-policy rule show -vserver " + v_server + " -policy "+ policy_name + " -fields policyname"
                time.sleep(3)
                stdin,stdout,stderr = ssh_client.exec_command(export_policy_cmd)
                time.sleep(5)
                output_rul_pol = stdout.read().decode().strip()
                if len(output_rul_pol) == 0 or re.search('There are no entries matching your query', output_rul_pol):
                    msg = "NO ACL and No Rule"
                    msg_output = "No ACL and rule entries from rule check for policy " + policy_name

                else:
                    msg ="Rule exist"
                    msg_output = output_rul_pol

    else:
        list_out = list(output.split(" "))
        list_out = [i for i in list_out if i]
        #print(list_out)
        #print(list_out[-1])
        del list_out[0 :14]
        if  len(list_out) != 0 and list_out[0] == "-" :
            msg = "NO ACL and No Rule"
            msg_output = "No ACL and rule need to check"
              ####################### include rules check here ####################
            time.sleep(3)
            stdin,stdout,stderr = ssh_client.exec_command(vol_policy_cmd)
            time.sleep(5)
            output_vol_pol = stdout.read().decode().strip()
                #print(output_vol_pol)
########################## checking if the volume has export policy ###################
            if  len(output_vol_pol) == 0 or re.search('There are no entries matching your query', output_vol_pol):
                msg = "NO ACL and No Rule"
                msg_output = "No ACL and rule entries volume check"
            else:
                list_out_vol = list(output_vol_pol.split(" "))
                list_out_vol = [i for i in list_out_vol if i]
                del list_out_vol[0 :12]
                policy_name = list_out_vol[0]
                    #print(list_out_vol)
                if  len(list_out_vol) == 1 and list_out_vol[0] == "-" :
                    msg = "NO ACL and No Rule"
                    msg_output = "No ACL and rule entries from - volume check "
                else:
                    export_policy_cmd = "export-policy rule show -vserver " + v_server + " -policy "+ policy_name + " -fields policyname"
                    time.sleep(3)
                    stdin,stdout,stderr = ssh_client.exec_command(export_policy_cmd)
                    time.sleep(5)
                    output_rul_pol = stdout.read().decode().strip()

                    if len(output_rul_pol) == 0 or re.search('There are no entries matching your query', output_rul_pol):
                        msg = "NO ACL and No Rule"
                        msg_output = "No ACL and rule entries from rule check for policy " + policy_name

                    else:
                        msg ="Rule exist"
                        msg_output = output_rul_pol
        else:
            msg = "ACL EXIST"
            msg_output =  output
    ssh_client.close()
    return msg,msg_output
        #print(msg,msg_output)



#fetch_cifs_acl(username,password,storage_box,vol_name,v_server)

def main():
    returnvalue = {}
    fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "storage_box":{"required":True,"type":"str"},
                "vol_name":{"required":True,"type":"str"},
                "v_server":{"required":True,"type":"str"},
        }
    module = AnsibleModule(argument_spec = fields)

    try:
        username = module.params["username"]
        password = module.params["password"]
        storage_box = module.params["storage_box"]
        vol_name = module.params["vol_name"]
        v_server = module.params["v_server"]
        acl_rule_fetch  =fetch_cifs_acl(username,password,storage_box,vol_name,v_server)
        returnvalue["acl_rule_output"] = acl_rule_fetch
        module.exit_json(** returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "[Error] "+str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    main()
