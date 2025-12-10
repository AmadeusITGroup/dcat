class CloseTaskAPI():

    def __init__(self, module):
        self.module = module
        self.endpoint = 'aproach-api/v1.0/taskrecords/'
        self.method = "PUT"

    def construct_request(self, operation, api_payload):

        payload, endpoint = self.construct_payload(operation, api_payload)
        return payload, endpoint, self.method

    def construct_payload(self, operation, api_payload):
        payload = {}

        if 'operation' not in payload:
            payload['operation'] = operation
        if 'taskRecord' not in payload:
            payload['taskRecord'] = {}
        if 'Overview' not in payload:
            payload['taskRecord']['Overview'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if 'text' == k:
                    payload['taskRecord']['Overview']['text'] = v
                elif 'task_id' == k:
                    self.endpoint = self.endpoint + v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload, self.endpoint
