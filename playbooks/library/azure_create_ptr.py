from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_ptr(hostname,cr,event_number,event,event_status,created_on,last_update,connection_string):
    
    table_name = "TRdetails"
    service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)

    try:   
        ptr_detail = service.get_entity(partition_key=hostname, row_key=event_number)
    except Exception as e:
        ptr_detail = None

    idempotent_obj = {}

    ### UPDATE / GET PTR ENTRY ###
    if ptr_detail:

        ci_name = ptr_detail['PartitionKey']
        ci_event_num = ptr_detail['RowKey']
        ci_cr = ptr_detail['cr']
        ci_event = ptr_detail['event']
        ci_event_status = ptr_detail['event_status']
        ci_created_on = ptr_detail['created_on']
        ci_last_update = ptr_detail['last_update']
        ci_event_type = ptr_detail['event_type']

        if event_status != ci_event_status:
            
            new_ent = {'RowKey':event_number,'PartitionKey':hostname,'cr':cr,'event':event,'event_type':'PTR',
                        'event_status':event_status,'created_on':created_on,'last_update':last_update} 
            
            temp = service.upsert_entity(mode=UpdateMode.MERGE, entity=new_ent)

            idempotent_obj['hostname'] = hostname
            idempotent_obj['cr'] = cr
            idempotent_obj['event_type'] = 'PTR'
            idempotent_obj['event_number'] = event_number
            idempotent_obj['event'] = event
            idempotent_obj['event_status'] = event_status
            idempotent_obj['created_on'] = created_on
            idempotent_obj['last_update'] = last_update

        else:

            idempotent_obj['hostname'] = ci_name
            idempotent_obj['cr'] = ci_cr
            idempotent_obj['event_type'] = ci_event_type
            idempotent_obj['event_number'] = ci_event_num
            idempotent_obj['event'] = ci_event
            idempotent_obj['event_status'] = ci_event_status
            idempotent_obj['created_on'] = ci_created_on
            idempotent_obj['last_update'] = ci_last_update


    ### NEW ENTRY FOR PTR ###    
    else:  
        
        new_ent = {'RowKey':event_number,'PartitionKey':hostname,'cr':cr,'event':event,'event_type':'PTR',
                    'event_status':event_status,'created_on':created_on,'last_update':last_update} 
            
        temp = service.create_entity(new_ent)

        idempotent_obj['hostname'] = hostname
        idempotent_obj['cr'] = cr
        idempotent_obj['event_type'] = 'PTR'
        idempotent_obj['event_number'] = event_number
        idempotent_obj['event'] = event
        idempotent_obj['event_status'] = event_status
        idempotent_obj['created_on'] = created_on
        idempotent_obj['last_update'] = last_update
    
    return idempotent_obj


def run_module():

    fields = {
        "hostname":{"required":True,"type":"str"},
        "cr":{"required":True,"type":"str"},
        "event_number":{"required":True,"type":"str"},
        "event":{"required":True,"type":"str"},
        "event_status":{"required":True,"type":"str"},
        "created_on":{"required":True,"type":"str"},
        "last_update":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_ptr(  hostname= module.params["hostname"],cr=module.params["cr"],
                                        event_number= module.params["event_number"],event= module.params["event"],
                                        event_status= module.params["event_status"],created_on=module.params["created_on"],
                                        last_update= module.params["last_update"],connection_string= module.params["connection_string"])
        if module_update:
            returnvalue["module_update"] = module_update
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["module_update"] = module_update
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["module_update"]="Exception occurred while creating entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()