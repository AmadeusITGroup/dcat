# Maintained by Kaushal

from azure.data.tables import TableClient, UpdateMode
from ansible.module_utils.basic import AnsibleModule
from azure.core.exceptions import ResourceNotFoundError

def update_entity(connection_string, table_name, partition_key, row_key, field_name, updated_value):
    """
    Updates a specified field in the Azure Table entity.
    """
    service = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
    try:
        # Fetch the entity to get the current data (We are assuming it's already there)
        entity = service.get_entity(partition_key=partition_key, row_key=row_key)
        
        # Update the specified field dynamically
        entity[field_name] = updated_value
        
        # Commit the updated entity back to the table
        service.update_entity(entity, mode=UpdateMode.MERGE)
        
        return {"status": "Entity updated successfully", "entity": entity}
    except ResourceNotFoundError:
        return {"status": "Entity not found"}
    except Exception as e:
        return {"status": f"An error occurred: {e}"}

def run_module():
    fields = {
        "connection_string": {"required": True, "type": "str"},
        "table_name": {"required": True, "type": "str"},
        "partition_key": {"required": True, "type": "str"},
        "row_key": {"required": True, "type": "str"},
        "field_name": {"required": True, "type": "str"},  # Add this parameter
        "updated_value": {"required": True, "type": "str"},  # Add this parameter
    }
    
    module = AnsibleModule(argument_spec=fields)
    result = {}

    try:
        # Update the entity field
        result = update_entity(
            connection_string=module.params["connection_string"],
            table_name=module.params["table_name"],
            partition_key=module.params["partition_key"],
            row_key=module.params["row_key"],
            field_name=module.params["field_name"],
            updated_value=module.params["updated_value"]
        )
        
        result['changed'] = True
        module.exit_json(**result)
        
    except Exception as err:
        result["status"] = f"Exception occurred: {err}"
        module.fail_json(**result)


if __name__ == '__main__':
    run_module()
