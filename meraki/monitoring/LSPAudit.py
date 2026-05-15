from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import requests
from meraki.settings.secret import devKey, prodKey, env
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from meraki.orgs import orgs
from datetime import datetime

# Relevant checks:
# 1.Loop through orgs inventory devices checking against networks to validate any network with no claims before 11/05/2025
# 2.Generate list of networks that have no inventory before 11/05/2025
# 3.Loop through generated network list and check for networks with LSP passwords set using getNetworkSettings endpoint


headers = {
    "Authorization": f"Bearer {prodKey if env == 'prod' else devKey}",
    "Accept": "application/json"
}

def lspAudit(orgID, headers):
    orgUrl = "https://api.meraki.com/api/v1/organizations"
    checkDate = datetime.fromisoformat('2025-08-01T00:00:00Z')
    remediate = False
    response = f"Organization: {orgID['name']}\n"
    orgUrl= f"{orgUrl}/{orgID['id']}/configurationChanges"
    orgResponse = requests.get(headers=headers, url=orgUrl) #grabs networks in organization
    if orgResponse.status_code != 200:
        response += f"Error: {orgResponse.status_code} - {orgResponse.text}\n"
        return response
    orgResponse = orgResponse.json()
    for entry in orgResponse:
        if "Create network" in entry['label'] and datetime.fromisoformat(entry['ts'])>checkDate:
            newValue = json.loads(entry['newValue'])
            settingURL = f"https://api.meraki.com/api/v1/networks/{newValue['id']}/settings"
            setResponse = requests.get(headers=headers, url=settingURL)
            if setResponse.status_code == 200:
                setResponse = setResponse.json()
                passValue = setResponse['localStatusPage']['authentication']['passwordSet']
                if not passValue:
                    response += f"Network: {newValue['name']} needs LSP password set and network was created after {checkDate.strftime('%B %d, %Y')}\n"
                    remediate = True
            else:
                continue
    response += "\n"
    if remediate == True:
        return response
    return ""
            

# print(lspAudit(orgs[33],headers=headers))
def run_all_checks(org_list, output_filename="./meraki/results/lspAudit_check_output.txt", max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(lspAudit, org, headers): org for org in org_list}
        for future in as_completed(futures):
            org = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(f"Error checking {org['name']} ({org['id']}): {exc}\n")

    output = "\n\n".join(r.strip() for r in results if r and r.strip())
    if output:
        output += "\n"
    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write(output)

    print(f"Results written to {output_filename}")
    return output


if __name__ == "__main__":
    run_all_checks(orgs)

