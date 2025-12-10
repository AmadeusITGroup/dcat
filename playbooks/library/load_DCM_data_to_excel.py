from ansible.module_utils.basic import AnsibleModule
import openpyxl
import yaml
import pandas as pd
import ast

def load_dcm_to_excel(data_path: str, store_path: str):

    with open(data_path, 'r') as raw_file:
        lines = raw_file.readlines()
    
    formatted_dict = {}

    for line in lines:
        data = ast.literal_eval(line.strip())
        formatted_dict.update(data)

    with open(data_path, "w") as f:
        yaml.dump(formatted_dict, f, sort_keys=False)

    temp_path = "temp_excel.xlsx"
    
    with open(data_path, 'r') as f:
        server_data = yaml.safe_load(f)

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "DCM Server Data"

    headers = ["Room", "Server", "CI ID", "Serial Number", "Product Name", "Site", "Building", "Coordinate", "Bay Rack"]
    sheet.append(headers)

    for server, details in server_data.items():
        row = [
            details.get("room", ""),
            server,
            details.get("CI ID+", ""),
            details.get("SerialNumber", ""),
            details.get("ProductName+", ""),
            details.get("Site", ""),
            details.get("building", ""),
            details.get("coordinate", ""),
            details.get("bay_rack", "")
        ]
        sheet.append(row)

    wb.save(temp_path)

    df = pd.read_excel(temp_path)
    df_sorted = df.sort_values(by="Room")
    df_sorted.to_excel(store_path, index=False)


def run_module():
    fields = {
        "data_path": {"required": True, "type": "str"},
        "store_path": {"required": True, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)
    returnvalue = {}

    try:
        data_path = module.params["data_path"]
        store_path = module.params["store_path"]

        load_dcm_to_excel(data_path, store_path)

        returnvalue["msg"] = f"Excel file created successfully at {store_path}"
        returnvalue["changed"] = True
        module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["msg"] = f"Exception occurred while generating Excel file: {str(err)}"
        returnvalue["changed"] = False
        module.fail_json(**returnvalue)


if __name__ == '__main__':
    run_module()
