"""Manual script to upload test results to Jira Xray.

Usage:
    1. Create a .env file with XRAY_CLIENT_ID and XRAY_CLIENT_SECRET
    2. Run: uv run python upload_to_jira.py
    3. Or:  python upload_to_jira.py

Requires: python-dotenv, requests
"""

import requests
import os
from dotenv import load_dotenv


# 1. Load environment variables (defined in .env file)
load_dotenv()


# 2. Settings
CLIENT_ID = os.getenv("XRAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET")


# 2. Get Access Token
def get_access_token():
    url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    auth_res = requests.post(url, json=payload)
    token = auth_res.text.replace('"', '')
    return token


# 3. upload XML to Jira - replace SAQC with your project ID
def upload_report():
    token = get_access_token()
    url = "https://xray.cloud.getxray.app/api/v2/import/execution/junit?projectKey=SAQC"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/xml"
    }
    with open("report.xml", "rb") as report:
        response = requests.post(url, headers=headers, data=report)

    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    upload_report()
