#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: winaproach
short_description: Winaproch Module based on REST APIs
version_added: "1.1"
requirements:
    - Win@aproach REST API access    
options:
    system:
        description:
            - test - winaproach PPT
            - prod - winaproach Production   
        required: true
    type:
        description:
            -  task_record, problem_record or work_order
        required: true
    operation:
        description:
            - create, close, end, start etc...
        required: true
   fields:
        description:
            - Payload for REST API
        required: true
'''

EXAMPLES = '''
- name: Test with a message
    winaproach:
        system: test
        type: task_record
        operation: create
        username: "{{ winaproach_username }}"
        password: "{{ winaproach_password }}"
        fields:
          title: Test
          parent_id: 13504260
          ccat1: IS
          ccat2: AP
          ccat3: AM
          system_category: test
          tested: Y
          test_record_type: T
          test_record: 
          validation_duration: "00:10"
          fallback_duration: "02:10"
          duration_planned: "01:23:10"
          customer_support: N
          start_date:
          start_time:
          end_date:
          end_time:
          approvals:
            - group: OHT01TAS
              board: CDX
            - group: 1AXYZ
              board: XYZ
          ci:
            - bkxv0001
          overview: "This is a Pre Approved Create TR"
          valdation_text: "These are the validation Steps"
          installtion_text: "Implementation Plan"
          fallback_steps: "These are the Backout Steps"
    register: testout

  - name: pause
    pause:
       minutes: 1

  - name: Start Implementation
    winaproach:
      system: test
      type: task_record
      operation: start_implementation
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
        task_id: "{{ testout.json.recordId }}"
    register: start_implementation

  - name: pause
    pause:
      minutes: 1

  - name: Update Task
    winaproach:
      system: test
      type: task_record
      operation: update_overview
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
        task_id: "{{ testout.json.recordId }}"
        text: "Update API"
    register: update

  - name: Add attachment
    winaproach:
      system: test
      type: task_record
      operation: add_attachment
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
        task_id: "{{ testout.json.recordId }}"
        file_name: "abcd.txt"
        file_content: "Test"
        wingroup: "OHT01TAS"
        text: "This attachment contains the details of the FW"
    register: update

  - name: END Implementation
    winaproach:
      system: test
      type: task_record
      operation: end_implementation
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
          task_id: "{{ testout.json.recordId }}"
          text: "This is fully implementated"
    register: end_implementation

  - name: dump test output
    debug:
      msg: '{{ end_implementation }}'

  - name: pause
    pause:
       minutes: 1

  - name: start Validate Implementation
    winaproach:
      system: test
      type: task_record
      operation: validate
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
        task_id: "{{ testout.json.recordId }}"
        text: "validated through REST APIS"
    register: validation

  - name: dump test output
    debug:
      msg: '{{ validation }}'

  - name: Close Task
    winaproach:
      system: test
      type: task_record
      operation: close
      username: "{{ winaproach_username }}"
      password: "{{ winaproach_password }}"
      fields:
        task_id: "{{ testout.json.recordId }}"
        text: "Closed as fully implemented"
    register: close
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the module generates
    type: str
    returned: always
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.changemanagement import ChangeManagementRestAPI
from ansible.module_utils.search.search import Search

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            system=dict(type='str', required=True, choices=['test','prod']),
            type=dict(type='str', required=True, choices=['task_record', 'problem_record',
                                                          'work_order', 'search']),
            operation=dict(type='str', required=True, choices=['create', 'close', 'fail',
                                                               'start_implementation',
                                                               'end_implementation',
                                                               'fail_implementation',
                                                               'partial_implementation',
                                                               'validate',
                                                               'fail_validation', 'update_overview',
                                                               'add_attachment', 'search']),
            fields = dict(required=True, type='dict'),
            username=dict(required=False, type='str'),
            password=dict(required=False, type='str', no_log=True)
        ),
         required_together=['username', 'password'],
     )
    system = module.params["system"]
    type = module.params["type"]
    operation = module.params["operation"]
    fields = module.params["fields"]
    username = module.params.get('username', None)
    password = module.params.get('password', None)

    result = dict(changed=False, original_message='', message='')

    if type in "task_record" or type in "problem_record" or type in "work_order":
        change_mangement = ChangeManagementRestAPI(module, system, username, password)
        response = change_mangement.execute(type, operation, fields)
    elif type == "search":
        search = Search()
        if 'text' in fields:
            search.search_ccat1(fields['text'])
        response = search.get_final_result()

    result['original_message'] = module.params['operation']
    result['message'] = response

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
