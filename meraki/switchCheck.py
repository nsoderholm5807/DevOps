import requests
from secret import devKey, prodKey
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from orgs import orgs

# Relevant checks:
# Loop through networks in orgs
# check each switch in the network
# report a list of every switch that is configured for DHCP
headers = {
    "Authorization" : f"Bearer {prodKey}", # put prod or dev key here
    "Accept": "application/json"
    }


def switchCheck(orgID, headers):
    response = ""
    orgUrl = "https://api.meraki.com/api/v1/organizations"
    netUrl= f"{orgUrl}/{orgID['id']}/networks"
    netResponse = requests.get(headers=headers, url=netUrl) #grabs networks in organization
    if netResponse.status_code != 200:
        return response
    switchDeviceUrl = f"{orgUrl}/{orgID['id']}/devices?productTypes[]=switch"
    switchDeviceResponse = requests.get(headers=headers, url=switchDeviceUrl).json() #grabs switch settings for further checks
    netResponse = netResponse.json()
    response += f"ORG: '{orgID['name']}'\n"
    for network in netResponse:
        response += f"Network: '{network['name']}'\n"
        for switch in switchDeviceResponse:
            if network['id'] == switch['networkId']:
                getDeviceConfig = f"https://api.meraki.com/api/v1/devices/{switch['serial']}/managementInterface"
                switchConfig = requests.get(headers=headers, url=getDeviceConfig).json()
                if not switchConfig['wan1']['usingStaticIp']:
                    response += f"    Switch name: '{switch['name']}' with Serial: '{switch['serial']}' is configured DHCP\n"
    return response


def run_all_checks(org_list, output_filename="switch_check_output.txt", max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(switchCheck, org, headers): org for org in org_list}
        for future in as_completed(futures):
            org = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(f"Error checking {org['name']} ({org['id']}): {exc}\n")

    output = "\n".join(results)
    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write(output)

    print(f"Results written to {output_filename}")
    return output


if __name__ == "__main__":
    run_all_checks(orgs)