from azure.data.tables import TableClient, TableServiceClient, UpdateMode
import configparser
from ansible.module_utils.basic import AnsibleModule
import requests


def create_entity(connection_string):
    
    idem = []

    #tr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="TRdetails")
    #metadata_service = TableClient.from_connection_string(conn_str=connection_string,table_name="metadataDetails")
    # cr_service = TableClient.from_connection_string(conn_str=connection_string,table_name="CRdetails")
    host_service = TableClient.from_connection_string(conn_str=connection_string,table_name="hostDetails")
    #phy_service = TableClient.from_connection_string(conn_str=connection_string,table_name="PhysicalServerDetails")

    try:   
        #tr_detail = tr_service.list_entities()
        #metadata_detail = metadata_service.list_entities()
        # cr_detail = cr_service.list_entities()
        # host_detail = host_service.list_entities()
        #phy_detail = phy_service.list_entities()
        # for det in phy_detail:
        #     idem.append(det)
        ent = {'mucsapdmp01', 'qlikatvs00', 'nosivp009', 'pimtstweb1', 'pimtstvault1', 'mucsapdmd01', 'pimtstweb2', 'pimtstvault2', 'pimtstpsm1', 'pimtstpsm2'}
        for del_ent in ent:
            host_service.delete_entity(partition_key= del_ent[:2], row_key=del_ent)
            idem.append(f"Deleted entity: PartitionKey={del_ent[:2]}, RowKey={del_ent}")
        # for entity in tr_detail:
        #     partition_key = entity['PartitionKey']
        #     row_key = entity['RowKey']
        #     tr_service.delete_entity(partition_key=partition_key, row_key=row_key)
        #     idem.append(f"Deleted entity: PartitionKey={partition_key}, RowKey={row_key}")
            #print(f"Deleted entity: PartitionKey={partition_key}, RowKey={row_key}")

        # for entity in metadata_detail:
        #     partition_key = entity['PartitionKey']
        #     row_key = entity['RowKey']
        #     metadata_service.delete_entity(partition_key=partition_key, row_key=row_key)
        #     idem.append(f"Deleted entity: PartitionKey={partition_key}, RowKey={row_key}")

        # for entity in cr_detail:
        #     partition_key = entity['PartitionKey']
        #     row_key = entity['RowKey']
        #     cr_service.delete_entity(partition_key=partition_key, row_key=row_key)
        #     idem.append(f"Deleted entity: PartitionKey={partition_key}, RowKey={row_key}")

        # for entity in host_detail:
        #     partition_key = entity['PartitionKey']
        #     row_key = entity['RowKey']
        #     host_service.delete_entity(partition_key=partition_key, row_key=row_key)
        #     idem.append(f"Deleted entity: PartitionKey={partition_key}, RowKey={row_key}")

        # for entity in phy_detail:
        #     if 'sutdown_bgp' in entity:
        #         entity.pop('sutdown_bgp')
        #         partition_key = entity['PartitionKey']
        #         row_key = entity['RowKey']
        #         phy_service.upsert_entity(mode=UpdateMode.REPLACE, entity=entity)
        #         idem.append(f"Updated entity: PartitionKey={partition_key}, RowKey={row_key}")
            
    except Exception as e:
        idem.append(e)
        # host_detail = None
        # tr_detail = None
        # cr_detail = None
        # metadata_detail = None
        # phy_detail = None

    # try:   
    #     tr_detail = tr_service.query_entities(query_filter=query_filter)
    # except Exception as e:
    #     idem.append(e)
    #     tr_detail = None

    # host_detail = tr_service.list_entities()

    # idem.append(list(host_detail))

    # if tr_detail:
    #     for tr in tr_detail:
    #         if tr["event"] == 'Application removal validation' or tr["event"] == 'Server owner approval':
    #             idem.append(tr)
    #             tr_obj = {}
    #             cr = tr["cr_number"]
    #             idem.append(cr)
    #             query_filter_metadata = f"PartitionKey eq '{cr}'"
                
    #             metadata_detail = metadata_service.query_entities(query_filter=query_filter_metadata)

    #             idem.append(list(metadata_detail))

    # service = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
    # try:
    #     # Attempt to delete the entity
    #     service.delete_entity(row_key="ob7dx301", partition_key="ob")
    #     idem.append("Deleted entity with row_key='ob7dx301' and partition_key='ob'.")
    # except ResourceNotFoundError:
    #     idem.append("Entity not found. Could not delete.")
    # except Exception as e:
    #     idem.append(f"An error occurred while deleting entity: {e}")

    # # Fetch the entities in list format

    # idem=[]

    # table_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    
    # new_table = table_client.create_table(table_name=table_name)
    # idem.append({"table_name": new_table.table_name})
    #tr_service = TableClient.from_connection_string(conn_str=connection_string,table_name=table_name)
    
   # query_filter = "event_status eq 'open'"  #(RowKey eq owner_tr))

    # try:   
    #     tr_detail = tr_service.list_entities()
    #     for ent in tr_detail:
    #         idem.append(ent)

    # except Exception as e:
    #     tr_detail = None
    #     idem.append(tr_detail)
    
    return idem


def run_module():

    fields = {
        "connection_string":{"required":True,"type":"str"}
        #"table_name":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        module_update = create_entity(connection_string= module.params["connection_string"])
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