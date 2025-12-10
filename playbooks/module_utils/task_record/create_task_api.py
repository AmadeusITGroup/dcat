from ansible.module_utils.task_record.fields_map import FieldsMap

class CreateTaskAPI():

    def __init__(self, module):
        self.fields_map = FieldsMap()
        self.module = module
        self.endpoint = 'aproach-api/v1.0/taskrecords/'
        self.method = "POST"

    def construct_request(self, operation, api_payload):

        payload = self.construct_payload(operation, api_payload)
        return payload, self.endpoint, self.method

    def construct_payload(self, operation, api_payload):
        payload = {}

        if 'operation' not in payload:
            payload['operation'] = operation

        if 'taskRecord' not in payload:
            payload['taskRecord'] = {}

        if 'normalFields' not in payload['taskRecord']:
            payload['taskRecord']['normalFields'] = {}

        if 'cmdbItems' not in payload['taskRecord']:
            payload['taskRecord']['cmdbItems'] = []

        if "Overview" not in payload['taskRecord']:
            payload['taskRecord']['Overview'] = {}

        if "ValidationSteps" not in payload['taskRecord']:
            payload['taskRecord']['ValidationSteps'] = {}

        if "Installation" not in payload['taskRecord']:
            payload['taskRecord']['Installation'] = {}

        if "Backout" not in payload['taskRecord']:
            payload['taskRecord']['Backout'] = {}
        # set default value for CleanSLot
        payload['taskRecord']['normalFields']['CleanSlot'] = 'true'

        if api_payload:
            for k, v in api_payload.items():
                if "title" == k:
                    payload['taskRecord']['normalFields']['Title'] = v
                elif "parent_id" == k:
                    payload['taskRecord']['normalFields']['TaskParentID'] = v
                elif "ccat1" == k:
                    #ccat1 = self.fields_map.change_type_map(api_payload['ccat1'])
                    payload['taskRecord']['normalFields']['ChangeCat1'] = v
                elif "ccat2" == k:
                    #ccat2 = self.fields_map.sub_type_map(api_payload['ccat2'])
                    payload['taskRecord']['normalFields']['ChangeCat2'] = v
                elif "ccat3" == k:
                    #ccat3 =  self.fields_map.action_type(api_payload['ccat3'])
                    payload['taskRecord']['normalFields']['ChangeCat3'] = v
                elif "system_category" == k:
                    system_category = self.fields_map.system_category_map(v)
                    payload['taskRecord']['normalFields']['SystemCategory'] = system_category
                elif "tested" == k:
                    payload['taskRecord']['normalFields']['RATestingRequired'] = v
                elif "test_record_type" == k:
                    payload['taskRecord']['normalFields']['TestRecType'] = v
                elif "test_record" == k:
                    payload['taskRecord']['normalFields']['CCTestRecord'] = v
                elif "customer_support" == k:
                    payload['taskRecord']['normalFields']['CustomerSupport'] = v
                elif "validation_duration" == k:
                    validation_duration = v 
                    payload['taskRecord']['normalFields']['ValidationDuration'] =  validation_duration
                elif "fallback_duration" == k:
                    fallback_duration = v
                    payload['taskRecord']['normalFields']['FallbackExpectedDuration'] = fallback_duration
                elif "duration_planned" == k:
                    duration_planned = v
                    payload['taskRecord']['normalFields']['DurationPlanned'] = duration_planned
                elif "start_date" == k:
                    payload['taskRecord']['normalFields']['StartDate'] = v
                elif "start_time" == k:
                    payload['taskRecord']['normalFields']['StartTime'] = v
                elif "end_date" == k:
                    payload['taskRecord']['normalFields']['EndDate'] = v
                elif "end_time" == k:
                    payload['taskRecord']['normalFields']['EndTime'] = v
                elif "clean_slot" == k:
                    payload['taskRecord']['normalFields']['CleanSlot'] = v
                elif "approvals" == k:
                    if 'approvals' not in payload['taskRecord']:
                        payload['taskRecord']['approvals'] = []
                    for approval in api_payload['approvals']:
                        payload['taskRecord']['approvals'].append({"apprSection": approval['group'],
                                                                   "approvalBoard": approval['board']})
                elif "ci" == k:
                    for node in api_payload['ci']:
                        payload['taskRecord']['cmdbItems'].append({"confItemName": node})
                elif "overview" == k:
                    payload['taskRecord']['Overview']['text'] = v
                elif "valdation_text" == k:
                    payload['taskRecord']['ValidationSteps']['text'] = v
                elif "installtion_text" == k:
                    payload['taskRecord']['Installation']['text'] = v
                elif "fallback_steps" == k:
                    payload['taskRecord']['Backout']['text'] = v
                else:
                    self.module.fail_json(msg="Invalid field: " + k)

        return payload




