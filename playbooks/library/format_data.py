from collections import defaultdict
from ansible.module_utils.basic import AnsibleModule

def data_val(data_in): 
    grouped_data = defaultdict(lambda: {"CI": set(), "other_details": None, "numbers": set()})
    for item in data_in:
        ritm_id = item[0]
        ci = item[1][0] 
        numbers = item[-1]
        other_details = item[2:-1]
        if ci not in grouped_data[ritm_id]["CI"]:
            grouped_data[ritm_id]["CI"].add(ci)
            grouped_data[ritm_id]["other_details"] = other_details
        grouped_data[ritm_id]["numbers"].update(numbers)

    final_result = []
    for ritm_id, data in grouped_data.items():
        ci_list = list(data["CI"])
        ci_final = [ci_list[i:i+20] for i in range(0, len(ci_list), 20)] # 20 indicaties no of CIs per splitting 
        for ci_list in ci_final:
            final_result.append([ritm_id] + [ci_list] + data["other_details"] + [list(data["numbers"])])

    return final_result                    

def main():
    returnValue = {}
    fields = {     
        "data_in":{"required":True, "type":"list"}            
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        output = data_val(module.params["data_in"])
                    
        returnValue["output"] = output                         
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnValue["error"] = str(err)
        module.exit_json(**returnValue)              

if __name__ == '__main__':
    main()
