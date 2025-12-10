from ansible.module_utils.task_record.create_task_api import CreateTaskAPI
from ansible.module_utils.task_record.close_task_api import CloseTaskAPI
from ansible.module_utils.task_record.start_implementation_api import StartImplementationAPI
from ansible.module_utils.task_record.end_implementation_api import EndImplementationAPI
from ansible.module_utils.task_record.validation_api import ValidationAPI
from ansible.module_utils.task_record.update_api import UpdateAPI
from ansible.module_utils.task_record.add_attachment_api import AddAttachmentAPI
from ansible.module_utils.basic import AnsibleModule

class TaskRecord():
    def __init__(self, module):
        self.module = module

    def operation_to_map(self, operation):
        operation_map = {
                "create": "tr_pre_approved_create",
                #"close": "tr_closed_as_implemented",
                #"fail": "tr_closed_as_implementation_failed",
                "start_implementation": "tr_start_implementation",
                "end_implementation": "tr_fully_implemented",
                "fail_implementation": "tr_impl_ongoing_to_closed_as_impl_failed",
                "validate": "tr_validated_as_fully_implemented_v2",
                "fail_validation": "tr_validated_as_implementation_failed_v2",
                "update_overview": "tr_update_overview",
                "add_attachment": "tr_add_attachment"
        }
        operation_name = operation_map[operation]
        return operation_name

    def construct_request(self, operation, fields):

        if operation == "create":
            create_task_API = CreateTaskAPI(self.module)
            data_payload, endpoint, method = create_task_API.construct_request(self.operation_to_map(operation), fields)
        #elif operation == "close":
        #    close_task_API = CloseTaskAPI(self.module)
        #    data_payload, endpoint, method = close_task_API.construct_request(self.operation_to_map(operation), fields)
        #elif operation == "fail":
        #    close_task_API = CloseTaskAPI(self.module)
        #    data_payload, endpoint, method = close_task_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "start_implementation":
            start_imp_API = StartImplementationAPI(self.module)
            data_payload, endpoint, method = start_imp_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "end_implementation":
            end_impl_API = EndImplementationAPI(self.module)
            data_payload, endpoint, method = end_impl_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "fail_implementation":
            end_impl_API = EndImplementationAPI(self.module)
            data_payload, endpoint, method = end_impl_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "validate":
            validation_API = ValidationAPI(self.module)
            data_payload, endpoint, method = validation_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "fail_validation":
            validation_API = ValidationAPI(self.module)
            data_payload, endpoint, method = validation_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "update_overview":
            update_API = UpdateAPI(self.module)
            data_payload, endpoint, method = update_API.construct_request(self.operation_to_map(operation), fields)
        elif operation == "add_attachment":
            attachment_api = AddAttachmentAPI(self.module)
            data_payload, endpoint, method = attachment_api.construct_request(self.operation_to_map(operation), fields)
        else:
            self.module.fail_json(msg=operation + " is a invalid operation for task_record, available operations are:"
                                        " [create, close, fail, start_implementation, "
                                                  "end_implementation, fail_implementation,"
                                                  "update_overview, add_attachment, "
                                                  "validate, fail_validation]")

        return endpoint, method, data_payload
