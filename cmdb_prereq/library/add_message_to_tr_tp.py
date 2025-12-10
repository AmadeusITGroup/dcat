from ansible.module_utils.basic import AnsibleModule
from pyproach import api

DOCUMENTATION = r'''
---
module: add_message_to_TR

description: Create Win@Proach TR.

version_added: "2.0.0"

options:
    record_id:
        description: ID of the record that has to be closed.
        required: true
        type: str
    message:
        description: Message to be added to the TR.
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
- name: "Add message to TR"
      add_message_to_TR:
        record_id: "{{ create_tr_output.record_id }}"
        message: "This is a test message from ansible."
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
'''
RETURN = r'''
# Module return values
added_msg:
    description: Boolean indicating whether or not message was added to the TR successfully.
    type: bool 
    returned: always

msg:
    description: Status message.
    type: str
    returned: always
'''


def add_msg(api,id,message):
    tr = api.retrieve(id)
    try:
        if tr.is_closed():
            status = "TR was closed. Did not add message."
        else:
            tr.add_message(message)
            tr.save()
            status = "Added messages successfully"
        return status
    except:
        status = "Failed to add message to TR."
    return status

def run_module():
    fields = {
        "record_id":{"required":True, type:"str"},
        "message":{"required":True, type:"str"},
        "username":{"required":True, type:"str"},
        "password":{"required":True, type:"str"},
    }

    module = AnsibleModule(argument_spec = fields)
    returnvalue = {"msg":"", "added_msg":False}
    winaproach_api = api.Aproach(username = module.params["username"],
                                password = module.params["password"])

    try:
        add_msg(winaproach_api, module.params["record_id"], module.params["message"])
        returnvalue["msg"] = "Added message to TR: "+module.params["message"]
        returnvalue["added_msg"] = True
        module.exit_json(**returnvalue)
    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = str(err)
        returnvalue["added_msg"] = False
        module.fail_json(**returnvalue)

if __name__=='__main__':
    run_module()
