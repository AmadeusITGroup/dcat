from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(ci,cr,event_number,event_status,created_on,last_update,connection_string):
    
    tr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="TRdetails")

    idempotent_obj = {}

    try:   
        tr_detail = tr_service.get_entity(partition_key=ci, row_key=event_number)
    except Exception as e:
        tr_detail = None

    if tr_detail:
        
        ci_cr = tr_detail["cr_number"]
        tr_event_type = tr_detail["event_type"]
        tr_event_number = tr_detail["RowKey"]
        tr_event = tr_detail["event"]
        tr_status = tr_detail["event_status"]
        tr_created_on = tr_detail["created_on"]
        tr_last_update = tr_detail["last_updated"]
        ci_name = tr_detail["PartitionKey"]

        if (tr_status != event_status or tr_last_update != last_update) and ci_cr == cr:

            new_entry = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'TR','event':'Application removal validation',
                    'event_status': event_status,'created_on':created_on,'last_updated':last_update}

            temp = tr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
            idempotent_obj["cr"] = cr
            idempotent_obj["event_type"] = 'TR'
            idempotent_obj["event_number"] = event_number
            idempotent_obj["ci_event"] = 'Application removal validation'
            idempotent_obj["event_status"] = event_status
            idempotent_obj["created_on"] = created_on
            idempotent_obj["last_update"] = last_update
            idempotent_obj["ci"] = ci

        # elif tr_event_number != '0' and tr_status != 'F' and event_number != '0' and event_status != 'F' and ci_cr == cr:

        #     new_entry = {'PartitionKey':ci,'RowKey':'app_tr','cr_number':cr,'event_type':'TR','event_number':event_number,
        #             'event_status': event_status,'created_on':created_on,'last_updated':last_update}

        #     temp = tr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        #     idempotent_obj["cr"] = cr
        #     idempotent_obj["event_type"] = 'TR'
        #     idempotent_obj["event_number"] = event_number
        #     idempotent_obj["ci_event"] = 'app_tr'
        #     idempotent_obj["event_status"] = event_status
        #     idempotent_obj["created_on"] = created_on
        #     idempotent_obj["last_update"] = last_update
        #     idempotent_obj["ci"] = ci

        elif ci_cr != cr:

            new_entry = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'TR','event': 'Application removal validation',
                    'event_status': event_status,'created_on':created_on,'last_updated':last_update}

            temp = tr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
            idempotent_obj["cr"] = cr
            idempotent_obj["event_type"] = 'TR'
            idempotent_obj["event_number"] = event_number
            idempotent_obj["ci_event"] = 'Application removal validation'
            idempotent_obj["event_status"] = event_status
            idempotent_obj["created_on"] = created_on
            idempotent_obj["last_update"] = last_update
            idempotent_obj["ci"] = ci 

        # elif tr_event_number != '0' and tr_status != 'F' and event_number == '0' and event_status == 'F' and ci_cr != cr:
            
        #     new_entry = {'PartitionKey':ci,'RowKey':'app_tr','cr_number':cr,'event_type':'TR','event_number':event_number,
        #             'event_status': event_status,'created_on':created_on,'last_updated':last_update}

        #     temp = tr_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        #     idempotent_obj["cr"] = cr
        #     idempotent_obj["event_type"] = 'TR'
        #     idempotent_obj["event_number"] = event_number
        #     idempotent_obj["ci_event"] = 'app_tr'
        #     idempotent_obj["event_status"] = event_status
        #     idempotent_obj["created_on"] = created_on
        #     idempotent_obj["last_update"] = last_update
        #     idempotent_obj["ci"] = ci 
        
        else:
            idempotent_obj["cr"] = ci_cr
            idempotent_obj["event_type"] = tr_event_type
            idempotent_obj["event_number"] = tr_event_number
            idempotent_obj["ci_event"] = tr_event
            idempotent_obj["event_status"] = tr_status
            idempotent_obj["created_on"] = tr_created_on
            idempotent_obj["last_update"] = tr_last_update
            idempotent_obj["ci"] = ci_name
    else:    
        new_ent = {'PartitionKey':ci,'RowKey':event_number,'cr_number':cr,'event_type':'TR','event':'Application removal validation',
                    'event_status': event_status,'created_on':created_on,'last_updated':last_update}
        
        temp = tr_service.create_entity(new_ent)

        idempotent_obj = {}
        idempotent_obj["cr"] = cr
        idempotent_obj["event_type"] = 'TR'
        idempotent_obj["event_number"] = event_number
        idempotent_obj["ci_event"] = 'Application removal validation'
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
        "event_status":{"required":True,"type":"str"},
        "created_on":{"required":True,"type":"str"},
        "last_update":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(ci= module.params["ci"],cr=module.params["cr"],
                                             event_number= module.params["event_number"],
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