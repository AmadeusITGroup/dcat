from ansible.module_utils.basic import AnsibleModule

def data_update(data_in):

    results = {}

    for item in data_in:
        ritm_id = item[0]
        numbers = item[7]
        if ritm_id not in results:
            results[ritm_id] = numbers

    output = [[ritm_id, numbers] for ritm_id, numbers in results.items()]

    return output

def main():
    returnValue = {}
    fields = {     
        "data_in":{"required":True, "type":"list"}            
    }
    module = AnsibleModule(argument_spec = fields)  
    
    try:
        output = data_update(module.params["data_in"])
                    
        returnValue["output"] = output                         
        module.exit_json(** returnValue)                  
        
    except Exception as err:
        returnValue["error"] = str(err)
        module.exit_json(**returnValue)              

if __name__ == '__main__':
    main()    