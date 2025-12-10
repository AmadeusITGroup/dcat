class CreateProblemTaskAPI():

    def __init__(self, module):
        self.module = module
        self.endpoint = 'aproach-api/v1.0/problemtrackingrecords/'
        self.method = "POST"

    def construct_request(self, operation, api_payload):

        payload = self.construct_payload(operation, api_payload)
        return payload, self.endpoint, self.method

    def construct_payload(self, operation, api_payload):
        payload = {}
        if 'operation' not in payload:
            payload['operation'] = operation

        if 'problemTrackingRecord' not in payload:
            payload['problemTrackingRecord'] = {}

        if 'normalFields' not in payload['problemTrackingRecord']:
            payload['problemTrackingRecord']['normalFields'] = {}

        if 'StatusText' not in payload['problemTrackingRecord']:
            payload['problemTrackingRecord']['StatusText'] = {}

        if api_payload:
            for k, v in api_payload.items():
                if "severity_level" == k:
                    payload['problemTrackingRecord']['normalFields']['Severity'] = v
                elif "title" == k:
                   payload['problemTrackingRecord']['normalFields']['Title'] = v
                elif "location" == k:
                    payload['problemTrackingRecord']['normalFields']['Location'] = v
                elif "system_category" == k:
                    payload['problemTrackingRecord']['normalFields']['AsysCategory'] = v
                elif "active_system" == k:
                    payload['problemTrackingRecord']['normalFields']['ActiveSystem'] = v
                elif "urgency_code" == k:
                    payload['problemTrackingRecord']['normalFields']['UrgencyCode'] = v
                elif "ref_task_id" == k:
                    payload['problemTrackingRecord']['normalFields']['TRReference'] = v
                elif "wingroup" == k:
                    payload['problemTrackingRecord']['normalFields']['AssigneeGroup'] = v
                elif "text" == k:
                    payload['problemTrackingRecord']['StatusText']['text'] = v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload



