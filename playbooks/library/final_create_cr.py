from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(ci,cr,connection_string):
    
    #connection_string = "DefaultEndpointsProtocol=https;AccountName=awxdcatdev;AccountKey=p0GybDYuCXIFrNDCnO7drvoA0PieEwdrkEOJMoonf0UFMBWw//km5DqES942kyJ7NjZ4V+VShZXJ+ASttmsS3w==;EndpointSuffix=core.windows.net"
    cr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="CRdetails")

    idempotent_obj = {}

    try:   
        cr_detail = cr_service.get_entity(partition_key=cr, row_key=ci)
    except Exception as e:
        cr_detail = None

    if cr_detail:
        cr_number = cr_detail["PartitionKey"]
        ci_name = cr_detail["RowKey"]

        # if ci_name == 'F' or cr_number == 'F':

        #     new_entry = {'PartitionKey':cr,'RowKey':ci}

        #     temp = cr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        #     idempotent_obj["cr"] = cr
        #     idempotent_obj["ci"] = ci
        
        # else:
        idempotent_obj["cr"] = cr_number
        idempotent_obj["ci"] = ci_name

    else:    
        new_ent = {'PartitionKey':cr,'RowKey':ci}
        
        temp = cr_service.create_entity(new_ent)

        # idempotent_obj = {}
        idempotent_obj["cr"] = cr
        idempotent_obj["ci"] = ci

    return idempotent_obj


def run_module():

    fields = {
        "ci":{"required":True,"type":"str"},
        "cr":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(ci= module.params["ci"],cr=module.params["cr"],connection_string= module.params["connection_string"])
        if create_entity_result:
            returnvalue["create_entity_result"] = create_entity_result
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["create_entity_result"] = create_entity_result
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["create_entity_result"]="Exception occurred while creating entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()