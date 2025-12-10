from ansible.module_utils.basic import *
import paramiko
import time

DOCUMENTATION='''
    This script is used to confirm the san cleanup process for the respective host
'''

def san_confirm(username,password,ipaddr,hostname,portdisable):
    finaloutput = "False"
    try:
        lists = []
        first_lists = []
        host=ipaddr
        ali_cmd = "alishow" 
        zone_cmd = "zoneshow"
        port_cmd = "portshow -i"
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)
        time.sleep(1)
        stdin,stdout,stderr = ssh_client.exec_command(ali_cmd+" "+"*"+hostname+"* ;"+zone_cmd+" "+"*"+hostname+"*")
        time.sleep(2)
        cmd_out = stdout.read().decode() 
        for line in cmd_out.splitlines():
            values = line.replace("\t", "")
            first_lists.append(values)
        my_list = [element for element in first_lists if element]
        if len(my_list) == 2 and "does not exist" in my_list[0] and "does not exist" in my_list[1]:
            ali_zone_result = True
        else:
            ali_zone_result = False 

        if ali_zone_result == True:
            stdin,stdout,stderr = ssh_client.exec_command(port_cmd+" "+portdisable +" |" + " grep portName; " + port_cmd+" "+portdisable +" |" + " grep portHealth; "+port_cmd+" "+portdisable +" |" + " grep portDisableReason" )
            time.sleep(2)
            port_output = stdout.read().decode() 
            for i in port_output.split("\n"):
                lists.append(i.strip())
            ssh_client.close()
        else:
            ssh_client.close()
        my_list2 = [element for element in lists if element]
        if ali_zone_result == True and len(my_list2) == 3:    
            name_port = my_list2[0].split(":")[1].strip()
            health_port = my_list2[1].split(":")[1].strip()
            Disable_reason = my_list2[2].split(":")[1].strip()
            if name_port == "Unassigned" and health_port == "OFFLINE" and Disable_reason == "Persistently disabled port":
                finaloutput = "True"
                return finaloutput
            else:
                return finaloutput
    
        else:
            return finaloutput
    
    except Exception as e:
        ssh_client.close()
        finaloutput="Exception occurred: "+ipaddr+" "+str(e)
        return finaloutput
        
def main():
    returnValue = dict()
    try:
        fields = {
                "username":{"required":True, "type":"str"},
                "password":{"required":True,"type":"str","no_log":True},
                "ipaddr":{"required":True,"type":"str"},
                "hostname":{"required":True,"type":"str"},
                "port_name":{"required":True,"type":"str"},
        }
        module = AnsibleModule(argument_spec = fields)
        
        username = module.params["username"]
        password = module.params["password"]
        ip_addr = module.params["ipaddr"]
        hostname = module.params["hostname"]
        portdisable = module.params["port_name"]
        san_process_check = san_confirm(username,password,ip_addr,hostname,portdisable) 
        if san_process_check == "True" :
            returnValue["a_check"] = "san cleanup success"
            module.exit_json(** returnValue) 
        elif san_process_check=="False":
            returnValue["a_check"] = "san cleanup fail"
            module.exit_json(** returnValue)
        else:
            returnValue["a_check"] = san_process_check #"san cleanup fail"
            module.exit_json(** returnValue)            
    except Exception as e:
        returnValue["msg"] = "[Error] "+str(e)
        module.fail_json(**returnValue)  

if __name__ == '__main__':
    main() 
    