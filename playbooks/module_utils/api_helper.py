from ansible.module_utils.urls import fetch_url
import json

class ApiHelper():

    def __init__(self, module=None, url=None, username=None, password=None):
        self.module = module
        self.url = url
        self.username = username
        self.password = password
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if username is not None and password is not None:
            self.module.params['url_username'] = module.params['username']
            self.module.params['url_password'] = module.params['password']
            self.module.params['force_basic_auth'] = True

    def select_system(self, system):
        if system == "test":
            url = "https://WIN@PROACH_DEV_URL/"
        elif system == "prod":
            url = "https://WIN@PROACH_URL/"

        return url

    def request(self, endpoint, data, method):
        url = self.select_system(self.url)
        url = url + endpoint
        resp, info = fetch_url(self.module, url, data=json.dumps(data), headers=self.headers, method=method, timeout=60)
        status_code = info["status"]

        if status_code == 201 or status_code == 200:
                response_body = json.loads(resp.read())
                self.module.exit_json(changed=True, msg="Success", json=response_body)
        elif status_code == 401:
                self.module.fail_json(msg="Invalid credentials", http_status_code=status_code)
        elif status_code == 404:
                self.module.fail_json(msg="URL Doesn't exist", http_status_code=status_code)
        elif status_code == 422:
                self.module.exit_json(changed=False, msg="Already Available")
        else:
                err = info
                self.module.fail_json(msg="Passed", http_status_code=status_code, error=err, payload=data)
