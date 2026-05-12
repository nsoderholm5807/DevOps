from pathlib import Path
import sys
import pprint
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from meraki.settings.secret import devKey, prodKey, env

# Generates orgs.py file that is used by rest of scripts in repository.

headers = {
    "Authorization": f"Bearer {prodKey if env == 'prod' else devKey}",  # put prod or dev key here
    "Accept": "application/json"
}

def generateOrgs(headers):
    orgUrl = "https://api.meraki.com/api/v1/organizations"
    output_filename = f"./meraki/{'prod' if env == 'prod' else 'dev'}Orgs.py"
    response = requests.get(headers=headers, url=orgUrl).json()
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"orgs = ")
        f.write(pprint.pformat(response, indent=2))
        f.write("\n")
    print(f"Results written to {output_filename}")

generateOrgs(headers)