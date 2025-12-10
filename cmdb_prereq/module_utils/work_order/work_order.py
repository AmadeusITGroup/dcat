from ansible.module_utils.work_order.create_work_order_api import CreateWorkOrderAPI
from ansible.module_utils.work_order.update_overview_api import UpdateOverviewAPI
from ansible.module_utils.work_order.add_attachment_api import AddAttachmentAPI
from ansible.module_utils.work_order.assign_to_implemented_api import AssignToImplementedAPI
from ansible.module_utils.work_order.implemented_to_close_api import ImplementedToCloseAPI

class WorkOrder():
    def __init__(self, module):
        self.module = module

    def operation_to_map(self, operation):
        operation_map = {
                "create": "wo_simple_create",
                "update_overview": "wo_update_overview",
                "add_attachment": "wo_add_attachment",
                "end_implementation": "wo_assigned_to_implemented",
                "close": "wo_implemented_to_closed"
        }
        operation_name = operation_map[operation]
        return operation_name

    def construct_request(self, operation, fields):

        if operation == "create":
            create_work_order_API = CreateWorkOrderAPI(self.module)
            data_payload, endpoint, method = create_work_order_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "update_overview":
            update_work_oder_API = UpdateOverviewAPI(self.module)
            data_payload, endpoint, method = update_work_oder_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "add_attachment":
            add_attachment_API = AddAttachmentAPI(self.module)
            data_payload, endpoint, method = add_attachment_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "end_implementation":
            assign_to_imp_API = AssignToImplementedAPI(self.module)
            data_payload, endpoint, method = assign_to_imp_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "close":
            imp_to_close_API = ImplementedToCloseAPI(self.module)
            data_payload, endpoint, method = imp_to_close_API.construct_request(self.operation_to_map(operation), fields)
        else:
            self.module.fail_json(msg=operation + " is a invalid operation for work_order, available operations are:"
                                        " [create, update_overview, add_attachment, end_implementation, close]")
        return endpoint, method, data_payload
