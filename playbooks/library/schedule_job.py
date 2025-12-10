import requests, random
import json
import base64
from datetime import datetime 
from datetime import timedelta 
from datetime import date 
from ansible.module_utils.basic import AnsibleModule
import warnings
warnings.filterwarnings("ignore")

def get_random_ist_time():

  base_date = datetime.now().date() + timedelta(days=7)
  start_time = datetime.combine(base_date, datetime.min.time()) + timedelta(hours=23)  # 11:00 PM
  end_time = start_time + timedelta(hours=7)  # 6:00 AM next day
  delta_seconds = int((end_time - start_time).total_seconds())
  random_seconds = random.randint(0, delta_seconds)
  return start_time + timedelta(seconds=random_seconds)
  

def run_scheduler(id,cr,associated_ci,retention_days,grace_flag,requester_name,requester_group,ritm_number,pillar,mit_ticket,cis,user_name,pass_word):
  url = "https://{{AWX_URL}}/api/v2/job_templates/"+id+"/schedules/"
  
  # Step 1: Generate a random IST time
  random_ist_time = get_random_ist_time()

  # Step 2: Convert IST to UTC
  ist_offset = timedelta(hours=5, minutes=30)
  random_utc_time = random_ist_time - ist_offset

  # Step 3: Format UTC time for AWX scheduler
  target_dt = '{:%Y%m%dT%H%M%SZ}'.format(random_utc_time)

  payload = json.dumps({
    "rrule": "DTSTART:"+target_dt+" RRULE:FREQ=DAILY;INTERVAL=0;COUNT=1",
    "name": "DCAT DECO - Phase2 - CR:"+str(cr)+str(cis),
    "description": "DCAT DECO - Phase2",
    "extra_data": {
      "associated_cis": associated_ci,
      "cr": str(cr),
      "graceperiod_flag": grace_flag,
      "retention_days": retention_days,
      "requester_name": requester_name,
      "requester_group": requester_group,
      "ritm_number": ritm_number,
      "pillar": pillar, 
      "mit_ticket": mit_ticket, 
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
  username = user_name
  password = pass_word    
  credentials = f"{username}:{password}"
  encoded_credentials = base64.b64encode(credentials.encode()).decode()    
  headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_credentials}',
  }
  response = requests.request("POST", url, headers=headers, verify=False,data=payload)
  if response.status_code == 201:
      return "Scheduled"
  else:
      return "Scheduler Failed" + response.text


def run_module():
    returnvalue = {}
    fields = {
         "id":{"required":True, "type":"str"},
         "cr":{"required":True, "type":"int"},
         "associated_cis":{"required":True, "type":"list"},
         "retention_days":{"required":True, "type":"str"},
         "grace_flag":{"required":True, "type":"str"},
         "requester_name":{"required":True, "type":"str"},
         "requester_group":{"required":True, "type":"str"},
         "ritm_number":{"required":True, "type":"str"},
         "pillar":{"required":False, "type":"str"},
         "mit_ticket":{"required":False, "type":"str"},
         "cis":{"required":True, "type":"str"},
         "user_name":{"required":True, "type":"str"},
         "pass_word":{"required":True, "type":"str"}
    }
    module = AnsibleModule(argument_spec = fields)
    if module.params['pillar'] is None or module.params['pillar'] == '':
        module.params['pillar'] = 'F'
    try:
        scheduler_status = run_scheduler(module.params["id"],module.params["cr"],
                                         module.params["associated_cis"],module.params["retention_days"],
                                         module.params["grace_flag"],module.params["requester_name"],module.params["requester_group"],
                                         module.params["ritm_number"],module.params["pillar"],module.params["mit_ticket"],module.params["cis"],module.params["user_name"],module.params["pass_word"])
        returnvalue["Status"] = scheduler_status
        module.exit_json(**returnvalue)

    except Exception as err: # pylint: disable=broad-except
        returnvalue["Status"] = "Exception occurred" + str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()
