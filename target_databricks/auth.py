import threading
import requests
import json
from datetime import datetime, timedelta, timezone


class Auth:
    def __init__(self, target):
        self.__lock = threading.Lock()
        self.__config = dict(target.config)
        self.__config_path = target.config_file_path
        self.__host = self.__config.get("host")
        self.__client_id = self.__config.get("client_id")
        self.__client_secret = self.__config.get("client_secret")
        self.__refresh_token = self.__config.get("refresh_token")

        self.__is_oa_auth = self.__client_id is not None and self.__client_secret is not None and self.__refresh_token is not None

        self.__session = requests.Session()
        self.__access_token = None if self.__is_oa_auth else self.__config.get("access_token")
        self.__expires_at = None


    def ensure_access_token(self):
        if self.__access_token is None or self.__expires_at is None or self.__expires_at <= datetime.now(timezone.utc):
            response = self.__session.post(
                f"https://{self.__host}/oidc/v1/token",
                data={
                    "client_id": self.__client_id,
                    "client_secret": self.__client_secret,
                    "refresh_token": self.__refresh_token,
                    "grant_type": "refresh_token"
                },
            )

            if response.status_code != 200:
                raise Exception(response.text)

            data = response.json()

            self.__access_token = data["access_token"]
            self.__refresh_token = data["refresh_token"]
            self.__config["refresh_token"] = data["refresh_token"]
            self.__config["access_token"] = data["access_token"]

            with open(self.__config_path, "w") as outfile:
                json.dump(self.__config, outfile, indent=4)

            self.__expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=int(data["expires_in"]) - 10
            )

    def get_access_token(self):
        if self.__is_oa_auth:
            with self.__lock:
                self.ensure_access_token()

        return self.__access_token
    