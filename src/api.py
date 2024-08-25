import json
import requests
import pandas as pd
from datetime import datetime

def pprint(data: dict) -> None:
    """Pretty print the data"""
    print(json.dumps(data, indent=4))


class Api:
    def __init__(self, *, api_key: str, api_token: str) -> None:
        self._api_key = api_key
        self._api_token = api_token

        self._headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self._auth = {"api_key": self._api_key, "api_token": self._api_token}

        # Check if the credentials are valid
        assert self.test()["success"], "Invalid credentials"

    def test(self) -> dict:
        """/api/v0/auth/test"""
        url = "https://marketplace.tensordock.com/api/v0/auth/test"
        return requests.post(url, headers=self._headers, data=self._auth).json()

    def get_marketplace(self, *, minRAM: int = 1, minStorage: int = 1, minVRAM: int = 4, minGPUCount: int = 1, 
                        requiresRTX: bool = False, requiresGTX: bool = False, maxGPUCount: int = 8) -> dict:
        """"Query the marketplace"""
        url = "https://marketplace.tensordock.com/api/v0/client/deploy/hostnodes"

        # Add the parameters to the auth
        params = {
            "minRAM": minRAM, 
            "minStorage": minStorage, 
            "minVRAM": minVRAM, 
            "minGPUCount": minGPUCount, 
            "requiresRTX": requiresRTX, 
            "requiresGTX": requiresGTX, 
            "maxGPUCount": maxGPUCount
        }
        return requests.get(url, params=params).json()

    def get_node(self, hostnode_uuid):
        """Return the information of a specific node, the uuid is the one of the machine, not the dashboard"""
        url = f"https://marketplace.tensordock.com/api/v0/client/deploy/hostnodes/{hostnode_uuid}"
        return requests.get(url).json()
    
    def get_revenue(self):
        """Return the revenue of the user"""
        url = "https://marketplace.tensordock.com/api/v0/billing/revenue"
        return requests.post(url, headers=self._headers, data=self._auth).json()
            
    def get_summary(self, period: str | datetime | pd.Timestamp = "today"):
        """Return the summary of the user"""
        url = "https://marketplace.tensordock.com/api/v0/billing/summary"

        # Check the period
        if isinstance(period, (datetime, pd.Timestamp)):
            period = period.strftime("%Y-%m")
        elif period == "today":
            period = datetime.now().strftime("%Y-%m")
            
        # Add the period to the auth
        return requests.post(url, headers=self._headers, data={**self._auth, "period": period}).json()