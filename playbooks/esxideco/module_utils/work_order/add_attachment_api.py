import base64
from ansible.module_utils._text import to_text

class AddAttachmentAPI():

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

        if 'attachment' not in payload:
            payload['workOrder']['attachment'] = {}

        if 'Overview' not in payload:
            payload['workOrder']['Overview'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if 'file_name' == k:
                    payload['workOrder']['attachment']['attachmentName'] = v
                elif 'file_content' == k:
                    file_content = v
                    encodedBytes = base64.b64encode(file_content.encode("utf-8"))
                    encodedStr = to_text(encodedBytes)
                    payload['workOrder']['attachment']['fileContent'] = encodedStr
                elif 'wingroup' == k:
                    payload['workOrder']['attachment']['attachmentGroup'] = v
                elif 'text' == k:
                    payload['workOrder']['Overview']['text'] = v
                elif 'wo_id' == k:
                    self.endpoint = self.endpoint + v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload, self.endpoint
