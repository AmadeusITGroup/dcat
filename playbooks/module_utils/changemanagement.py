from ansible.module_utils.api_helper import ApiHelper
from ansible.module_utils.task_record.task_record import TaskRecord
from ansible.module_utils.problem_task_record.problem_task_record import ProblemTaskRecord
from ansible.module_utils.work_order.work_order import WorkOrder

class ChangeManagementRestAPI(object):
    def __init__(self, module=None, url=None, username=None, password=None):
        self.api_helper = ApiHelper(module, url, username, password)
        self.task_record = TaskRecord(module)
        self.problem_task_record = ProblemTaskRecord(module)
        self.work_order = WorkOrder(module)

    def execute(self, type, operation, fields):

        if type == "task_record":
            endpoint, method, data_payload = self.task_record.construct_request(operation, fields)
        elif type == "problem_record":
            endpoint, method, data_payload = self.problem_task_record.construct_request(operation, fields)
        elif type == "work_order":
            endpoint, method, data_payload = self.work_order.construct_request(operation, fields)
        self.result = self.api_helper.request(endpoint, data_payload, method)
        return self.result
