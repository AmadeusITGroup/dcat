class CreateWorkOrderAPI():

    def __init__(self, module):
        self.module = module
        self.endpoint = 'aproach-api/v1.0/workorders'
        self.method = "POST"

    def construct_request(self, operation, api_payload):
        payload = self.construct_payload(operation, api_payload)
        return payload, self.endpoint, self.method

    def construct_payload(self, operation, api_payload):
        payload = {}
        if 'operation' not in payload:
            payload['operation'] = operation

        if 'workOrder' not in payload:
            payload['workOrder'] = {}

        if 'normalFields' not in payload['workOrder']:
            payload['workOrder']['normalFields'] = {}

        if 'Overview' not in payload['workOrder']:
            payload['workOrder']['Overview'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if "severity_level" == k:
                    payload['workOrder']['normalFields']['Severity'] = v
                elif "title" == k:
                   payload['workOrder']['normalFields']['Title'] = v
                elif "type" == k:
                    payload['workOrder']['normalFields']['Type'] = v
                elif "system_category" == k:
                    payload['workOrder']['normalFields']['System'] = v
                elif "assignee_group" == k:
                    payload['workOrder']['normalFields']['AssigneeGroup'] = v
                elif "order_type" == k:
                    payload['workOrder']['normalFields']['WorkorderType'] = v
                elif "assignee_name" == k:
                    payload['workOrder']['normalFields']['AssigneeName'] = v
                elif "text" == k:
                    payload['workOrder']['Overview']['text'] = v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)
        return payload



