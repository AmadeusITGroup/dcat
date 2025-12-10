import requests
import json
import warnings
from ansible.module_utils.basic import AnsibleModule
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_freeze(oms_url,change_type_level1,change_type_level2,change_methods,hosts,environment):
  try:
      freeze_final_data ={}
      freeze=[]
      no_freeze=[]
      freeze_info = []
      result={}
      for data in hosts:
        url = "https://"+oms_url+"/oms/isFreezePresent"
        payload = json.dumps({
          "start_epoch": "",
          "end_epoch": "",
          "change_type_level1": change_type_level1,
          "change_type_level2": change_type_level2,
          "change_methods": change_methods,
          "item_list": data,
          "product_environment": environment
        })
        headers = {
          'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        output = response.json()
        if str(output['freeze_status']) == "True":
           result["info"] = output['details']
           result["hostname"] = data
           freeze_info.append(result)
           freeze.append(data)
        else:
           no_freeze.append(data)
      freeze_final_data["Freeze_list"] = freeze
      freeze_final_data["Freeze_information"] = freeze_info
      freeze_final_data["No_freeze"] = no_freeze
      return freeze_final_data
  except Exception as e:
    out="ERROR: " + str(e)
    return out

def run_module():
    fields = {
        "oms_url":{"required":True, "type":"str"},
        "change_type_level1":{"required":True, "type":"str"},
        "change_type_level2":{"required":True, "type":"str"},
        "change_methods":{"required":True, "type":"str"},
        "hosts":{"required":True, "type":"list"},
        "environment":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        freeze_status =  get_freeze(module.params["oms_url"],module.params["change_type_level1"],module.params["change_type_level2"],module.params["change_methods"],module.params["hosts"],module.params["environment"])
        returnvalue["status"] = freeze_status
        module.exit_json(**returnvalue)
    except Exception as err:
        returnvalue["status"]="Exception occurred " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()