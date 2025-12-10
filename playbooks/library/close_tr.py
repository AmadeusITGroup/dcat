from ansible.module_utils.basic import AnsibleModule
from pyproach import api
DOCUMENTATION = r'''
---
module: close_TR

description: Create Win@Proach TR.

version_added: "2.0.0"

options:
    record_id:
        description: ID of the record that has to be closed.
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

'''

EXAMPLES = r'''
- name: "Test custome module [CLOSE TR]"
      close_TR:
        record_id: "{{ record_id }}"
        username: "{{ creds.username }}"
        password: "{{ creds.password }}"
'''
RETURN = r'''
# Module return values
closed:
    description: Boolean indicating whether or not the record was closed successfully.
    type: bool 
    returned: always

msg:
    description: Status message.
    type: str
    returned: always
'''

def close_tr(api,id):
    try:
        tr = api.retrieve(id)
    except:
        raise RuntimeError("Failed to retrieve TR with ID: "+id)
    try:
        if not tr.is_closed():
            tr.close()
            tr.save()
    except:
        raise RuntimeError("Failed to close TR with ID: "+id)

def run_module():
    fields = {
        "record_id": {"required":True, type:"str"},
        "username":{"required":True, "type":"str","no_log":True},
        "password":{"required":True, "type":"str","no_log":True}
    }
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {
        "msg":"",
        "closed":False
    }

    winaproach_api = api.Aproach(username = module.params["username"],
                                password=module.params["password"])

    try:
        close_tr(winaproach_api, module.params["record_id"])
        returnvalue["msg"] = "Closed TR."
        returnvalue["closed"] = True
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["msg"] = str(err)
        returnvalue["closed"] = False
        module.fail_json(**returnvalue)

if __name__=='__main__':
    run_module()
    