import pprint
import requests
from secret import devKey, prodKey

# Generates orgs.py file that is used by rest of scripts in repository.

headers = {
    "Authorization": f"Bearer {prodKey}",  # put prod or dev key here
    "Accept": "application/json"
}

def generateOrgs(headers):
    orgUrl = "https://api.meraki.com/api/v1/organizations"
    output_filename = "./meraki/orgs.py"
    response = requests.get(headers=headers, url=orgUrl).json()
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("orgs = ")
        f.write(pprint.pformat(response, indent=2))
        f.write("\n")
    print(f"Results written to {output_filename}")

generateOrgs(headers)