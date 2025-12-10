class ImplementedToCloseAPI():

    def __init__(self, module):
        self.module = module
        self.endpoint = 'aproach-api/v1.0/workorders/'
        self.method = "PUT"

    def construct_request(self, operation, api_payload):

        payload, endpoint = self.construct_payload(operation, api_payload)
        return payload, endpoint, self.method

    def construct_payload(self, operation, api_payload):
        payload = {}
        if 'operation' not in payload:
            payload['operation'] = operation

        if 'workOrder' not in payload:
            payload['workOrder'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if "wo_id" == k:
                    self.endpoint = self.endpoint + v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload, self.endpoint
