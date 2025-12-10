import base64
from ansible.module_utils._text import to_text


class AddAttachmentAPI:
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
        if 'attachment' not in payload:
            payload['taskRecord']['attachment'] = {}
        if 'Overview' not in payload:
            payload['taskRecord']['Overview'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if 'file_name' == k:
                    payload['taskRecord']['attachment']['attachmentName'] = v
                elif 'file_content' == k:
                    file_content = v
                    encodedBytes = base64.b64encode(file_content.encode("utf-8"))
                    encodedStr = to_text(encodedBytes)
                    payload['taskRecord']['attachment']['fileContent'] = encodedStr
                elif 'wingroup' == k:
                    payload['taskRecord']['attachment']['attachmentGroup'] = v
                elif 'text' == k:
                    payload['taskRecord']['Overview']['text'] = v
                elif 'task_id' == k:
                    self.endpoint = self.endpoint + v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload, self.endpoint
