from azure.data.tables import TableClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule


def create_entity(cr,awx_job_id,ritm_number,requestor_name,retention_days,requestor_group,pillar,mit_ticket,cmdb,connection_string):
    
    #connection_string = "DefaultEndpointsProtocol=https;AccountName=<redacted>;EndpointSuffix=core.windows.net"
    metadata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="metadataDetails")

    idempotent_obj = {}

    try:   
        metadata_details = metadata_service.get_entity(partition_key=cr, row_key=awx_job_id)
    except Exception as e:
        metadata_details = None

    if metadata_details:
        cr_num = metadata_details["PartitionKey"]
        awx_id = metadata_details["RowKey"]
        ritm = metadata_details["ritm_number"]
        requestor = metadata_details["requestor_name"]
        retention = metadata_details["retention_days"]
        group_requested = metadata_details["requestor_group"]
        pillar_name = metadata_details["pillar"]
        mit_ticket = metadata_details["mit_ticket"]
        cmdb_status = metadata_details["cmdb"]
        
        # if ritm == 'F' or requestor == 'F' or retention == 'F' or group_requested == 'F' or cmdb_status =='F':

        #     new_entry = {'PartitionKey':cr,'RowKey':awx_job_id,'ritm_number':ritm_number,'requestor_name':requestor_name,'retention_days':retention_days,
        #             'requestor_group': requestor_group,'cmdb':cmdb}

        #     temp = metadata_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
        #     idempotent_obj["cr"] = cr
        #     idempotent_obj["awx_job_id"] = awx_job_id
        #     idempotent_obj["ritm_number"] = ritm_number
        #     idempotent_obj["requestor_name"] = requestor_name
        #     idempotent_obj["retention_days"] = retention_days
        #     idempotent_obj["requestor_group"] = requestor_group
        #     idempotent_obj["cmdb"] = cmdb
        
        # else:

        if cmdb_status =='F'and cmdb != 'F':

            new_entry = {'PartitionKey':cr,'RowKey':awx_job_id,'cmdb':cmdb}

            temp = metadata_service.upsert_entity(mode=UpdateMode.MERGE, entity=new_entry)
            idempotent_obj["cr"] = cr
            idempotent_obj["awx_job_id"] = awx_job_id
            idempotent_obj["ritm_number"] = ritm_number
            idempotent_obj["requestor_name"] = requestor_name
            idempotent_obj["retention_days"] = retention_days
            idempotent_obj["requestor_group"] = requestor_group
            idempotent_obj["pillar"] = pillar
            idempotent_obj["mit_ticket"] = mit_ticket
            idempotent_obj["cmdb"] = cmdb
        
        else:        
            idempotent_obj["cr"] = cr_num
            idempotent_obj["awx_job_id"] = awx_id
            idempotent_obj["ritm_number"] = ritm
            idempotent_obj["requestor_name"] = requestor
            idempotent_obj["retention_days"] = retention
            idempotent_obj["requestor_group"] = group_requested
            idempotent_obj["pillar"] = pillar_name
            idempotent_obj["mit_ticket"] = mit_ticket
            idempotent_obj["cmdb"] = cmdb_status
    else:    
        new_ent = {'PartitionKey':cr,'RowKey':awx_job_id,'ritm_number':ritm_number,'requestor_name':requestor_name,
                    'retention_days':retention_days,'requestor_group': requestor_group,'pillar': pillar,'mit_ticket': mit_ticket,'cmdb':'F'}
        
        temp = metadata_service.create_entity(new_ent)

        idempotent_obj = {}
        idempotent_obj["cr"] = cr
        idempotent_obj["awx_job_id"] = awx_job_id
        idempotent_obj["ritm_number"] = ritm_number
        idempotent_obj["requestor_name"] = requestor_name
        idempotent_obj["retention_days"] = retention_days
        idempotent_obj["requestor_group"] = requestor_group
        idempotent_obj["pillar"] = pillar
        idempotent_obj["mit_ticket"] = mit_ticket
        idempotent_obj["cmdb"] = 'F'

    return idempotent_obj


def run_module():

    fields = {
        "cr":{"required":True,"type":"str"},
        "awx_job_id":{"required":True,"type":"str"},
        "ritm_number":{"required":True,"type":"str"},
        "requestor_name":{"required":True,"type":"str"},
        "retention_days":{"required":True,"type":"str"},
        "requestor_group":{"required":True,"type":"str"},
        "pillar":{"required":False,"type":"str"},
        "mit_ticket":{"required":False,"type":"str"},
        "cmdb":{"required":True,"type":"str"},
        "connection_string":{"required":True,"type":"str"}
    }

    if pillar == "":
        pillar = 'F'
    if mit_ticket == "":
        mit_ticket = 'F'
            
    module = AnsibleModule(argument_spec = fields)
    if module.params['pillar'] is None or module.params['pillar'] == '':
        module.params['pillar'] = 'F'
    returnvalue = {}
    
    try:
        
        create_entity_result = create_entity(cr= module.params["cr"],awx_job_id=module.params["awx_job_id"],
                                             ritm_number= module.params["ritm_number"],requestor_name=module.params["requestor_name"],
                                             retention_days= module.params["retention_days"],requestor_group=module.params["requestor_group"],
                                             pillar= module.params["pillar"],mit_ticket= module.params["mit_ticket"],cmdb= module.params["cmdb"],
                                             connection_string= module.params["connection_string"])
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