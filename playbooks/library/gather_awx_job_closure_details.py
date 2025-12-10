import configparser,requests
from requests.auth import HTTPBasicAuth
from ansible.module_utils.basic import AnsibleModule


def job_fetch(awx_jobs,curr_awx_job,awx_instance,awx_username,awx_password):

    idempotent_obj={}
    
    awx_job_flag=True

    for job_id in awx_jobs:

        if job_id != curr_awx_job:
           
            url = "https://"+awx_instance+"/api/v2/jobs/"+job_id+"/"
            try:
                response = requests.get(url, auth=HTTPBasicAuth(awx_username, awx_password), verify=False)
                job_details = response.json()
                if response.status_code == 200:
                    job_status = job_details.get('status')
                    
                    if job_status != "successful":
                        awx_job_flag = False
                    else:
                        pass
                else:
                    awx_job_flag = False
                    idempotent_obj= "Exception occured " + str(job_details)
            except Exception as e:
                awx_job_flag=False
                idempotent_obj= "Exception occured " + str(e)
            
        else:
            pass


    if awx_job_flag == True:
        idempotent_obj = "SUCCESS"
    else:
        idempotent_obj = "FAILURE"

    return idempotent_obj


def run_module():

    fields = {
        "awx_jobs":{"required":True,"type":"list"},
        "curr_awx_job":{"required":True,"type":"str"},
        "awx_instance":{"required":True,"type":"str"},
        "awx_username":{"required":True,"type":"str"},
        "awx_password":{"required":True,"type":"str"}
    }
    
    module = AnsibleModule(argument_spec = fields)
    returnvalue = {}
    
    try:
        
        create_entity_result = job_fetch(   awx_jobs= module.params["awx_jobs"],curr_awx_job= module.params["curr_awx_job"],
                                            awx_instance= module.params["awx_instance"],
                                            awx_username= module.params["awx_username"],awx_password= module.params["awx_password"])
        if create_entity_result:
            returnvalue["create_entity_result"] = create_entity_result
            returnvalue['changed'] = True
            module.exit_json(**returnvalue)
        else:
            returnvalue["create_entity_result"] = create_entity_result
            module.exit_json(**returnvalue)

    except Exception as err:
        returnvalue["create_entity_result"]="Exception occurred while creating entity.Kindly check. " +str(err)
        module.exit_json(**returnvalue)

if __name__ == '__main__':
    run_module()