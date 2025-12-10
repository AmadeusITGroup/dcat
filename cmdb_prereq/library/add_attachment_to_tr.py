from ansible.module_utils.basic import AnsibleModule
from pyproach import api

DOCUMENTATION = r'''
---
module: add_attachment_to_TR

description: Add attachments to TR.

version_added: "2.0.0"

options:
    record_id:
        description: ID of the record that has to be closed.
        required: true
        type: str
    attachments:
        description: Path of attachments to be added.
        required: true
        type: list
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
- name: "Add attachments to TR"
      add_attachment_to_TR:
        record_id: "{{ create_tr_output.record_id }}"
        attachments: "{{ atachments }}
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
'''
RETURN = r'''
# Module return values
added_attachments:
    description: Boolean indicating whether or not attachments were added to the TR successfully.
    type: bool 
    returned: always

msg:
    description: Status message.
    type: str
    returned: always
'''


def add_attachments(api,id,attachments):
    tr = api.retrieve(id)
    if tr.is_closed():
        status = "TR was closed. Did not add attachment(s)."
    else:
        tr.add_attachments(attachments)
        tr.save()
        status = "TR was closed. added attachment(s)."
    return status
def run_module():
    fields = {
        "record_id":{"required":True, "type":"str"},
        "attachments":{"required":True, "type":"list"},
        "username":{"required":True, "type":"str"},
        "password":{"required":True, "type":"str"},
    }

    module = AnsibleModule(argument_spec = fields)
    returnvalue = {"msg":"", "added_attachments":False}
    winaproach_api = api.Aproach(username = module.params["username"],
                                password=module.params["password"])
    try:
        add_attachments(winaproach_api,module.params["record_id"],module.params["attachments"])
        returnvalue["msg"] = "Added attachment(s) to TR: "+module.params["record_id"]
        returnvalue["added_attachments"] = True
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = "Failed to add attachments: "+str(err)
        module.fail_json(**returnvalue)

if __name__=='__main__':
    run_module()
