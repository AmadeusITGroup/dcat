from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(connection_string):
    
    #connection_string = "DefaultEndpointsProtocol=https;AccountName=awxdcatdev;AccountKey=p0GybDYuCXIFrNDCnO7drvoA0PieEwdrkEOJMoonf0UFMBWw//km5DqES942kyJ7NjZ4V+VShZXJ+ASttmsS3w==;EndpointSuffix=core.windows.net"
    ptr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="TRdetails")
    metadata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="metadataDetails")

    query_filter = "event_status eq 'open' and event_type eq 'PTR'"  #(RowKey eq owner_tr))
    idempotent_obj = []

    try:   
        ptr_detail = ptr_service.query_entities(query_filter=query_filter)
    except Exception as e:
        ptr_detail = None

    
    if ptr_detail:
        for ptr in ptr_detail:
            ptr_obj = {}
            cr = ptr["cr_number"]
            query_filter_metadata = f"PartitionKey eq '{cr}'"
            
            metadata_detail = metadata_service.query_entities(query_filter=query_filter_metadata)
            
            for obj in metadata_detail:
                awx_job_id = obj["RowKey"]
                ritm_number = obj["ritm_number"]
                requestor_name = obj["requestor_name"]
                retention_days = obj["retention_days"]
                requestor_group = obj["requestor_group"]
                cmdb = obj["cmdb"]
                pillar = obj["pillar"]
                
            tr_event_type = ptr["event_type"]
            tr_event_number = ptr["RowKey"]
            tr_event = ptr["event"]
            tr_status = ptr["event_status"]
            tr_created_on = ptr["created_on"]
            tr_last_update = ptr["last_updated"]
            ci = ptr["PartitionKey"]

            ptr_obj["cr"] = cr
            ptr_obj["event_type"] = tr_event_type
            ptr_obj["event_number"] = tr_event_number
            ptr_obj["ci_event"] = tr_event
            ptr_obj["event_status"] = tr_status
            ptr_obj["created_on"] = tr_created_on
            ptr_obj["last_update"] = tr_last_update
            ptr_obj["ci"] = ci
            ptr_obj["awx_job_id"] = awx_job_id
            ptr_obj["ritm_number"] = ritm_number
            ptr_obj["requestor_name"] = requestor_name
            ptr_obj["retention_days"] = retention_days
            ptr_obj["requestor_group"] = requestor_group
            ptr_obj["cmdb"] = cmdb
            ptr_obj["pillar"] = pillar
            
            idempotent_obj.append(ptr_obj)
        
    

    return idempotent_obj


def run_module():

    fields = {
        "connection_string":{"required":True,"type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(connection_string= module.params["connection_string"])
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