from ansible.module_utils.basic import AnsibleModule

def set_group(path):
    dict1={}
    dict2={}
    with open(path) as f:
      for line in f:
        (key, val) = line.split()
        dict1[key] = val
    dict2 = {n:[k for k in dict1.keys() if dict1[k] == n] for n in set(dict1.values())}
    return dict2

def run_module():
    fields = {
         "path":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    try:
        group_path = set_group(path = module.params["path"])
        returnvalue["Status"] = group_path
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = "Exception occurred while categorizing CI's. " + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
