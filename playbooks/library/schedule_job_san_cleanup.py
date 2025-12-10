import requests
import json
from datetime import datetime 
from datetime import timedelta 
from datetime import date 
from ansible.module_utils.basic import AnsibleModule
import warnings
warnings.filterwarnings("ignore")

def run_scheduler(cr,id,associated_ci,retention_days,graceperiod_flag,ritm_number,requester_name,requester_group):
  url = "https://{{AWX_URL}}/api/v2/job_templates/"+id+"/schedules/"
  date = datetime.now() + timedelta(hours=25)
  dt = '{:%Y%m%d}'.format(date)
  hr= '{:%H%M%S}'.format(date)
  target_dt = dt+"T"+hr+"Z"
  payload = json.dumps({
    "rrule": "DTSTART:"+target_dt+" RRULE:FREQ=DAILY;INTERVAL=0;COUNT=1",
    "name": "DCAT DECO - SAN Cleanup Schedule - CR:"+str(cr),
    "description": "DCAT DECO - SAN Cleanup Schedule worflow",
    "extra_data": {
      "associated_cis": associated_ci,
      "cr": str(cr),
      "graceperiod_flag": graceperiod_flag,
      "retention_days": retention_days,
      "requester_name": requester_name,
      "ritm_number": ritm_number,
      "requester_group": requester_group, 
    },
    "inventory": None,
    "scm_branch": "",
    "job_type": None,
    "job_tags": "",
    "skip_tags": "",
    "limit": "",
    "diff_mode": False,
    "verbosity": None,
    "execution_environment": None,
    "forks": None,
    "job_slice_count": None,
    "timeout": None,
    "enabled": True
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 5q7Kzfg447XEjN8y6A6JKQvA1lXB1e',
  }
  response = requests.request("POST", url, headers=headers, verify=False,data=payload)
  if response.status_code == 201:
      return "Scheduled"
  else:
      return "Scheduler Failed" + response.text  

def run_module():
    returnvalue = {}
    fields = {
         "cr":{"required":True, "type":"int"},
         "id":{"required":True, "type":"str"},
         "associated_cis":{"required":True, "type":"list"},
         "retention_days":{"required":True, "type":"str"},
         "graceperiod_flag":{"required":True, "type":"str"},
         "requester_name":{"required":True, "type":"str"},
         "ritm_number":{"required":True, "type":"str"},
         "requester_group":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    try:
        scheduler_status = run_scheduler(module.params["cr"],module.params["id"],
                                         module.params["associated_cis"],module.params["retention_days"],module.params["ritm_number"],
                                         module.params["graceperiod_flag"],module.params["requester_name"],module.params["requester_group"]
                                         )
        returnvalue["Status"] = scheduler_status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = "Exception occurred" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()