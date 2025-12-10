from ansible.module_utils.problem_task_record.create_problem_task import CreateProblemTaskAPI

class ProblemTaskRecord():

    def __init__(self, module):
        self.module = module

    def operation_to_map(self, operation):
        operation_map = {
                "create": "ptr_simple_create",
        }
        operation_name = operation_map[operation]
        return operation_name

    def construct_request(self, operation, fields):
        if operation == "create":
            create_problem_API = CreateProblemTaskAPI(self.module)
            data_payload, endpoint, method = create_problem_API.construct_request(self.operation_to_map(operation), fields)
        else:
            self.module.fail_json(msg=operation + " is a invalid operation for problem_record, available operations are:"
                                        " [create]")

        return endpoint, method, data_payload
