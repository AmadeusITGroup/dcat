from ansible.module_utils.basic import AnsibleModule
import pandas as pd
import json
import ast
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
#pd.set_option('display.expand_frame_repr', False)


# host="vmdecovt005"
# cmdb_rtu=""{{CMDB_URL}}""

def run_module():
    returnvalue = {}
    try:
        fields = {
            "host":{"required":True, "type":"str"},
            "cmdb_rtu":{"required":True, "type":"str"}
        }
        module = AnsibleModule(argument_spec = fields)
        vm_list=[]
        phy_list=[]
        host_list=[]
        info = module.params["host"]
        cmdb_rtu = module.params["cmdb_rtu"]
        val = json.dumps(info)
        value = ast.literal_eval(val)
        result = json.loads(value)
        for val in result:
            host_list.append(val['hosts'])
        for val in host_list:
            url = "https://"+cmdb_rtu+"/rtu/?serverName="+val.lower()
            data_frame = pd.read_json(url)
            if data_frame.empty or val=="":
                msg ="No Entry Available for host in RTU"
            else:
                if data_frame.iloc[0]['serverIsVirtual'] == 'Yes':
                  vm_list.append(val)
                else:
                    phy_list.append(val)
        returnvalue["vm_list"] = vm_list
        returnvalue["phy_list"] = phy_list
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["diff_host"] = "Exception occurred" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
