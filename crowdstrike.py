import json
import requests


class Crowdstrike:

    def __init__(self, client_id:str, client_secret:str) -> None:
        self.batch_id = None
        self.hosts = []
        self.hosts_metadata = []
        self.base_url = "https://api.crowdstrike.com"
        self.session = self.__authenticate(client_id, client_secret)
        self.session_timeout = 30
        self.errors = []

    def __authenticate(self, client_id:str, client_secret:str) -> requests.Session:
        session = requests.Session()
        session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        session.headers["Accept"] = "application/json"

        data = { "client_id": client_id,
                 "client_secret": client_secret
        }

        response = session.post("{}/oauth2/token".format(self.base_url), data=data)

        if response.status_code != 201:
            print("[!] Failed to authenticate")
            self.errors = [response.json()]
            return None
        else:
            self.errors = []
        
        session.headers["Authorization"] = "Bearer {}".format(response.json().get("access_token"))
        session.headers["Content-Type"] = "application/json"
        
        return session

    def get_host_ids(self, limit:int=100) -> None:
        params = { "limit": limit,
                   "offset": 0
        }

        response = self.session.get("{}/devices/queries/devices/v1".format(self.base_url), params=params)

        if response.status_code != 200:
            print("[!] Failed to get hosts from get_host_ids")
            self.errors = [response.json()]
        else:
            self.errors = []
            self.hosts = [host for host in response.json().get('resources')]

    def get_host_information(self) -> None:
        params = { "ids": self.hosts}

        response = self.session.get("{}/devices/entities/devices/v1".format(self.base_url), params=params)

        if response.status_code != 200:
            print("failed to get hosts from get_host_information")
            self.errors = [response.json()]
        else:
            self.errors = []
            self.hosts_metadata = response.json().get("resources") 

    def set_session(self, hosts_list:list, queue_if_offline:bool=True) -> None:
        data = json.dumps({ "host_ids": hosts_list,   
                            "queue_offline": queue_if_offline
                          })
        
        response = self.session.post("{}/real-time-response/combined/batch-init-session/v1?timeout={}&timeout_duration={}s".format(
                                        self.base_url, 
                                        self.session_timeout, 
                                        self.session_timeout), 
                                     data=data)

        if response.status_code == 404:
            print(response.json().get("errors")[0].get("message"))
            self.errors = [response.json()]
        elif response.status_code != 201:
            print("failed to set session")
            self.errors = [response.json()]
        else:
            self.errors = []
            self.batch_id = response.json().get("batch_id")

    def run_command(self, base_command:str, command_options:str, persist:bool=True) -> dict:
        self.errors = []
        data = json.dumps({ "batch_id": self.batch_id, 
                            "base_command": base_command, 
                            "command_string": command_options, 
                            "persist_all": persist
                          })

        response = self.session.post("{}/real-time-response/combined/batch-admin-command/v1?timeout={}&timeout_duration={}s".format(
                                        self.base_url, 
                                        self.session_timeout, 
                                        self.session_timeout), 
                                     data=data)

        if response.status_code != 201:
            self.errors = [response.json()]
            return {}
        else:
            resources = response.json().get('combined').get("resources")
            for k, v in resources.items():
                if v.get("errors") != [] or v.get("stderr") != "":
                    for host in self.hosts_metadata:
                        if host.get("device_id") == k:
                            self.errors.append({"id": k, 
                                                "error": v.get("errors"), 
                                                "stderr": v.get("stderr"), 
                                                "hostname": host.get("hostname")
                                              })

            return resources
