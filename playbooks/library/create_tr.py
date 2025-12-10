from ansible.module_utils.basic import AnsibleModule
from pyproach import api
DOCUMENTATION = r'''
---
module: create_TR

description: Create Win@Proach TR.

version_added: "2.0.0"

options:
    record_type:
        description: Type of record.
        required: true
        type: str
    title:
        description: Title of TR.
        required: true
        type: str
    assignee_group:
        description: Group to which this TR will be assigned to.
        required: false
        type: str
    assignee_name:
        description: Person to whom this TR will be assigned to.
        required: true
        type: str
    severity:
        description: Severity of the TR.
        required: true
        type: str
    overview:
        description: TR overview.
        required: true
        type: str
    username:
        description: Username of service account used to interact with Win@Proach.
        required: true
        type: str
    password:
        description: Password of service account used to interact with Win@Proach.
        required: true
        type: str

author:
    - Thineshkumar R (@thr)
'''

EXAMPLES = r'''
# Module usage example 
- name: "Test custom module [CREATE TR]"
      create_TR:
        record_type: "TR"
        title: "pyproach test"
        assignee_name: "L. T L"
        severity: "4"
        overview: "from ansible"
        username: "username"
        password: "password"
'''

RETURN = r'''
# Module return values
title:
    description: Title of created TR.
    type: str
    returned: When TR creation is successful

msg:
    description: Error message.
    type: str
    returned: When TR creation fails.
'''

def create_tr(api, record_type, title,assignee_name, severity, overview, parent_id, assignee_group):
    new_ptr = api.create_record(
        record_type = record_type,
        title = title,
        assignee_name = assignee_name,
        severity = severity,
        overview = overview,
        parent_id = parent_id,
        assignee_group = assignee_group
    )
    new_ptr.save()
    return new_ptr.id


def run_module():
    fields = {
        "record_type": {"required":True, type:"str"},
        "title": {"required":True, type:"str"},
        "assignee_name": {"required":True, type:"str"},
        "severity": {"required":True, type:"str"},
        "overview": {"required":True, type:"str"},
        "parent_id": {"required":True, type:"str"},
        "assignee_group": {"required":True, type:"str"},
        "username": {"required":True, type:"str","no_log":True},
        "password": {"required":True, type:"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {"title":module.params["title"]}
    winaproach_api = api.Aproach(username = module.params["username"],
                                password = module.params["password"])
    try:
        record_id = create_tr(
            api = winaproach_api,
            record_type = module.params["record_type"],
            title = module.params["title"],
            assignee_name = module.params["assignee_name"],
            severity = module.params["severity"],
            overview = module.params["overview"],
            parent_id = module.params["parent_id"],
            assignee_group=module.params["assignee_group"]
        )
    except Exception as err: # pylint: disable=broad-except
        module.fail_json(msg = str(err))
    returnvalue["record_id"] = record_id
    module.exit_json(** returnvalue)
if __name__=='__main__':
    run_module()
    