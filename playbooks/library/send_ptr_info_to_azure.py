from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(ci,cr,event_number,event, event_status,created_on,last_update,connection_string):
    
    ptr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="TRdetails")

    idempotent_obj = {}

    try:   
        ptr_detail = ptr_service.get_entity(partition_key=ci, row_key=event_number)
    except Exception as e:
        ptr_detail = None

    if ptr_detail:
        
        ci_cr = ptr_detail["cr_number"]
        ptr_event_type = ptr_detail["event_type"]
        ptr_event_number = ptr_detail["RowKey"]
        ptr_event = ptr_detail["event"]
        ptr_status = ptr_detail["event_status"]
        ptr_created_on = ptr_detail["created_on"]
        ptr_last_update = ptr_detail["last_updated"]
        ci_name = ptr_detail["PartitionKey"]

        if (ptr_status != event_status or ptr_last_update != last_update) and ci_cr == cr:

            new_entry = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'PTR',
                    'event_status': event_status, 'last_updated':last_update}

            temp = ptr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
            idempotent_obj["cr"] = cr
            idempotent_obj["event_type"] = 'PTR'
            idempotent_obj["event_number"] = event_number
            idempotent_obj["event_status"] = event_status
            idempotent_obj["created_on"] = created_on
            idempotent_obj["last_update"] = last_update
            idempotent_obj["ci"] = ci

        elif ci_cr != cr:

            new_entry = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'PTR',
                    'event_status': event_status, 'last_updated':last_update}

            temp = ptr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
            idempotent_obj["cr"] = cr
            idempotent_obj["event_type"] = 'PTR'
            idempotent_obj["event_number"] = event_number
            idempotent_obj["event_status"] = event_status
            idempotent_obj["created_on"] = created_on
            idempotent_obj["last_update"] = last_update
            idempotent_obj["ci"] = ci 
        
        else:
            idempotent_obj["cr"] = ci_cr
            idempotent_obj["event_type"] = ptr_event_type
            idempotent_obj["event_number"] = ptr_event_number
            idempotent_obj["ci_event"] = ptr_event
            idempotent_obj["event_status"] = ptr_status
            idempotent_obj["created_on"] = ptr_created_on
            idempotent_obj["last_update"] = ptr_last_update
            idempotent_obj["ci"] = ci_name
    else:    
        new_ent = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'PTR','event': event,
                    'event_status': event_status,'created_on':created_on,'last_updated':last_update}
        
        temp = ptr_service.create_entity(new_ent)

        idempotent_obj = {}
        idempotent_obj["cr"] = cr
        idempotent_obj["event_type"] = 'PTR'
        idempotent_obj["event_number"] = event_number
        idempotent_obj["ci_event"] = event
        idempotent_obj["event_status"] = event_status
        idempotent_obj["created_on"] = created_on
        idempotent_obj["last_update"] = last_update
        idempotent_obj["ci"] = ci

    return idempotent_obj


def run_module():

    fields = {
        "ci":{"required":True,"type":"str"},
        "cr":{"required":True,"type":"str"},
        "event_number":{"required":True,"type":"str"},
        "event":{"required":False,"type":"str"},
        "event_status":{"required":True,"type":"str"},
        "created_on":{"required":True,"type":"str"},
        "last_update":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(ci= module.params["ci"],cr=module.params["cr"],
                                             event_number= module.params["event_number"], event= module.params["event"],
                                             event_status= module.params["event_status"],created_on=module.params["created_on"],
                                             last_update= module.params["last_update"],connection_string= module.params["connection_string"])
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