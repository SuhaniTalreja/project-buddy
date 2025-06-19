import os
from dotenv import load_dotenv
import requests

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USERNAME")

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Check if it can access your user details
resp = requests.get("https://api.github.com/user", headers=headers)

if resp.status_code == 200:
    print("✅ GitHub API authentication successful!")
    print(f"Logged in as: {resp.json()['login']}")
else:
    print("❌ GitHub authentication failed")
    print(resp.text)
