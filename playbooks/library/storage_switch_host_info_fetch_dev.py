import sys, os, string, threading
import paramiko
import time
import re
import itertools
from concurrent.futures import ThreadPoolExecutor
from ansible.module_utils.basic import AnsibleModule
import warnings
warnings.filterwarnings("ignore")

 
outlock = threading.Lock()
 
# host_wwpn =  ["10:00:9c:dc:71:72:7d:d3"] #, '10:00:9c:dc:71:72:7d:d4', '10:00:9c:dc:71:72:7d:df','10:00:9c:dc:71:72:7d:e0', '10:00:9c:dc:71:72:9e:67', '10:00:9c:dc:71:72:9e:68'] 
def parallel_run(host,host_name_deco,username,password):   
    first_lists=[]
    alias_list=[]
    my_list_port=[]
    port_list=[]
    zone_lists=[]
    my_list=[]
    file_name= "wwpn"+host_name_deco+".txt"
    fabric_list=[]
    switch_info_result_list=[]
    with open(file_name) as fh:
        host_wwpn = fh.readlines()
    fabric_cmd = "fabricshow"   
    cfg_cmd = "cfgshow | more"    
    result_list=[]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host,username=username,password=password,port=22)
    time.sleep(2)
    for wwp in host_wwpn:
      first_lists=[]
      alias_list=[]
      my_list_port=[]
      port_list=[]
      zone_lists=[]
      my_list=[]
      fabric_list=[]
      switch_info_result_list=[]
      wwpn=wwp.strip()
      node_cmd = "nodefind "+wwpn 
      zone_cmd = "nszoneshow -wwn "+wwpn
      stdin, stdout, stderr = ssh_client.exec_command(node_cmd)
      node_cmd_out = stdout.read().decode() 
      for line in node_cmd_out.splitlines():
        values = line.replace("\t", "")
        first_lists.append(values)
      my_list = [element for element in first_lists if element]
      if "No device found" in my_list: 
        result= "no device found for switch " +host+" for wwpn "+wwpn
        switch_info_result="no device"
        result_list.append(result)
        #print(result_list)      
      else: 
        pid_value = node_cmd_out.split('\n')[1]
        pattern = r'\s(\w+);' #pattern match to fetch the PID value before 1st ; in the output
        match = re.search(pattern, pid_value)
        if match:
          pid = match.group(1)
          pid_hex = pid[0:2]
          pid_dec = int(pid_hex,16)
          pid_final = str(pid_dec)+":"
        else:
          pid_final = " "
        if len(pid_final) == 0:               
            pid_switch_info_name="no information of pid hence no switch name"
        else:
            pid_info=pid_final
            stdin,stdout,stderr = ssh_client.exec_command(fabric_cmd)
            time.sleep(2)
            fabric_cmd_out = stdout.read().decode()    
            with open('output_fabric_info.txt','w') as file:
              file.write(fabric_cmd_out)  
            with open('output_fabric_info.txt') as fh:
              file_content = fh.readlines()
              for line in file_content:    
                # ip = re.match(rf"\s*?{pid_info}", line)
                ip = re.match(r"\s*?{}".format(pid_info), line)
                if ip:
                  regexp = re.compile("\"(.*)\"$")
                  if regexp:
                    pid_switch_name=regexp.search(line).group(1)
                    pid_switch_info=pid_switch_name+fqdn                                
                  else:
                    pid_switch_info = "no information for switch name"               
                else:
                    pid_switch_info = "no information for switch name" 
              pid_switch_info = [switch_name for switch_name in pid_switch_info if 'mucfs' in switch_name or 'frafs' in switch_name]
              fabric_list.append(pid_switch_info)
            with open('output_fabric_info.txt','w') as file:
               file.truncate(0)       
            pid_switch_info_filtered=[item for item in fabric_list if "no information" not in item]  
            if len(pid_switch_info_filtered)== 0:
               pid_switch_info_name="no information for switch name"
            else:
               pid_switch_info_name=pid_switch_info_filtered  

            ############ fetching port index ###########
        port_index_pattern = r"Port Index: (\d+)"
        port_matches = re.findall(port_index_pattern,node_cmd_out)
        if len(port_matches)== 0:               
          port_info=[] #"no information of port"
        else:
          port_info=port_matches       
            # ###########  fetching aliases ##################################################
        aliases_pattern = r"Aliases: (\w+)"
        alias_matches = re.findall(aliases_pattern,node_cmd_out)
        if len(alias_matches)== 0:
          alias_info =[]
        else:
          alias_info=alias_matches 
            # ############## Fetching the zone names ##########################################
        stdin,stdout,stderr = ssh_client.exec_command(zone_cmd)
        time.sleep(2)
        zone_cmd_out = stdout.read().decode() 
        for line_zone in zone_cmd_out.splitlines():
            values_zone = line_zone.replace("\t", "")
            zone_lists.append(values_zone)
        my_list_zone = [element for element in zone_lists if element]   
        if "Zone Names" not in my_list_zone: 
            zone_info=[] #"no information of zone"
        else:     
            del my_list_zone[0:2] 
            del my_list_zone[-1]   
            if len(my_list_zone)== 0:
                zone_info=[] #"no information of zone"   
            else:
                zone_info=my_list_zone
                zone_info=[item.strip() for item in zone_info]  

            # ######################## fetching fabric name from cfg command ##################
        stdin,stdout,stderr = ssh_client.exec_command(cfg_cmd)
        time.sleep(2)
        cfg_cmd_out = stdout.read().decode() 
        cfg_pattern = r"cfg:\s*?(\w+)"
        cfg_matches = re.findall(cfg_pattern,cfg_cmd_out)
        if len(cfg_matches)== 0:
          cfg_info =[] #"no information from cfg for fabric name"
        else:
          cfg_info=cfg_matches
          cfg_info=list(set(cfg_info))              

            #########  seggregating all the information fetched to a single list variable ###################                           
        if "no information" in pid_switch_info_name or [] in port_info or [] in zone_info or [] in cfg_info:
            result= host,wwpn,pid_switch_info_name,port_info,alias_info,zone_info,cfg_info
            switch_info_result="no information"
            result_list.append(result)
        else: 
            switch_info_result="success"   
            result = host,wwpn,pid_switch_info_name,port_info,alias_info,zone_info,cfg_info#,zone_info
            result_list.append(result) 
    ssh_client.close()
    return result_list 


def par(host_name,host_name_deco,username,password):
  with ThreadPoolExecutor() as executor:
      output = list(executor.map(parallel_run,host_name,[host_name_deco]*len(host_name),[username]*len(host_name),[password]*len(host_name)))
  return output  

def run_module():
    returnvalue = {}
    fields = {
         "host":{"required":True, "type":"list"},
         "hostname":{"required":True, "type":"str"},
         "username":{"required":True, "type":"str"},
         "password":{"required":True, "type":"str"}         
    }
    module = AnsibleModule(argument_spec = fields)
    host_name = module.params["host"]
    host_name_deco = module.params["hostname"]
    username = module.params["username"]
    password = module.params["password"]    

    try:
      output_final=par(host_name,host_name_deco,username,password)
      returnvalue["status"] = output_final
      module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["status"] = "Exception occurred : " + str(err)
        # returnvalue["hos"] = host_wpn
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()