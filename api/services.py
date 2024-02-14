import os
import requests
from urllib.parse import quote_plus as urlencode

class MetadataCenterAPIService:

    def __init__(self):
        self.api_key = os.getenv("METADATACENTER_KEY")
        self.base_url = "https://resource.metadatacenter.org"
        self.headers = {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json"
        }

    def __request_get(self, path, params=None):
        url = f"{self.base_url}/{path}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def __request_post(self, path, data):
        url = f"{self.base_url}/{path}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_instances(self, folder_id, page = 1):
        limit = 100
        offset = (page - 1) * limit

        folder_path = f"https://repo.metadatacenter.org/folders/{folder_id}"
        return self.__request_get(f"folders/{urlencode(folder_path)}/contents?offset={offset}&limit={limit}")

    def get_instance(self, instance_id):
        instance_path = f"https://repo.metadatacenter.org/template-instances/{instance_id}"
        return self.__request_get(f"template-instances/{urlencode(instance_path)}")
