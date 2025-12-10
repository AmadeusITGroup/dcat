from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(connection_string):
    
    #connection_string = "DefaultEndpointsProtocol=https;AccountName=awxdcatdev;AccountKey=p0GybDYuCXIFrNDCnO7drvoA0PieEwdrkEOJMoonf0UFMBWw//km5DqES942kyJ7NjZ4V+VShZXJ+ASttmsS3w==;EndpointSuffix=core.windows.net"
    tr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="TRdetails")
    metadata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="metadataDetails")

    query_filter = "event_status eq 'open'"  #(RowKey eq owner_tr))
    idempotent_obj = []

    try:   
        tr_detail = tr_service.query_entities(query_filter=query_filter)
    except Exception as e:
        tr_detail = None

    
    if tr_detail:
        for tr in tr_detail:
            if tr["event"] == 'Application removal validation' or tr["event"] == 'Server owner approval':
                tr_obj = {}
                cr = tr["cr_number"]
                query_filter_metadata = f"PartitionKey eq '{cr}'"
                
                metadata_detail = metadata_service.query_entities(query_filter=query_filter_metadata)

                #host_metadata_detail = list(metadata_detail)

                for obj in metadata_detail:
                    if obj:
                       # idempotent_obj.append(obj)
                        awx_job_id = obj["RowKey"]
                        ritm_number = obj["ritm_number"]
                        requestor_name = obj["requestor_name"]
                        retention_days = obj["retention_days"]
                        requestor_group = obj["requestor_group"]
                        cmdb = obj["cmdb"]
                        pillar = obj["pillar"]

                        tr_obj["awx_job_id"] = awx_job_id
                        tr_obj["ritm_number"] = ritm_number
                        tr_obj["requestor_name"] = requestor_name
                        tr_obj["retention_days"] = retention_days
                        tr_obj["requestor_group"] = requestor_group
                        tr_obj["cmdb"] = cmdb
                        tr_obj["pillar"] = pillar
                    else:
                        pass
                    
                tr_event_type = tr["event_type"]
                tr_event_number = tr["RowKey"]
                tr_event = tr["event"]
                tr_status = tr["event_status"]
                tr_created_on = tr["created_on"]
                tr_last_update = tr["last_updated"]
                ci = tr["PartitionKey"]

                tr_obj["cr"] = cr
                tr_obj["event_type"] = tr_event_type
                tr_obj["event_number"] = tr_event_number
                tr_obj["ci_event"] = tr_event
                tr_obj["event_status"] = tr_status
                tr_obj["created_on"] = tr_created_on
                tr_obj["last_update"] = tr_last_update
                tr_obj["ci"] = ci
                
                
                idempotent_obj.append(tr_obj)
        
    

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