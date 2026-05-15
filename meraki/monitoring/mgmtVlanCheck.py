from pathlib import Path
import sys
import requests
from meraki.settings.secret import devKey, prodKey, env
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from meraki.orgs import orgs

# Relevant checks: 
# 1.Does MGMT vlan exist? Done 
# 2.Does it match switch settings MGMT vlan? Done
# 3.Does the switch settings have the core switch set as the root? Done
# 4.Are the switches staticly assigned to MGMT vlan? Done

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

headers = {
    "Authorization": f"Bearer {prodKey if env == 'prod' else devKey}",
    "Accept": "application/json"
}


def mgmtCheck(orgID,headers):
    response = f"{orgID['name']}\n\n"
    orgUrl = "https://api.meraki.com/api/v1/organizations"
    netUrl= f"{orgUrl}/{orgID['id']}/networks"
    netResponse = requests.get(headers=headers, url=netUrl) #grabs networks in organization
    if netResponse.status_code != 200:
        response += f"Error: {netResponse.status_code} - {netResponse.text}\n"
        return response
    netResponse = netResponse.json()
    for network in netResponse:
        if all(check in network['productTypes'] for check in ('appliance', 'switch')): #validates network as MX and MS devices for further checks
            switchDeviceUrl = f"{orgUrl}/{orgID['id']}/devices?productTypes[]=switch"
            switchDeviceResponse = requests.get(headers=headers, url=switchDeviceUrl).json() #grabs switch settings for further checks
            getVlanUrl = f"https://api.meraki.com/api/v1/networks/{network['id']}/appliance/vlans"
            vlanResponse = requests.get(headers=headers, url=getVlanUrl) #grabs vlan settings on MX
            if vlanResponse.status_code != 200:
                response += f"  VLAN Error for network {network['name']}: {vlanResponse.status_code} - {vlanResponse.text}\n\n"
                continue
            getVlans = vlanResponse.json()
            MGMTvlan = False
            for vlans in getVlans:
                if any(mcheck in vlans['name'].lower() for mcheck in ('management', 'mgmt')): #checks for existance of management Vlan
                    switchUrl= f"https://api.meraki.com/api/v1/networks/{vlans['networkId']}/switch/settings"
                    switchResponse = requests.get(headers=headers, url=switchUrl).json()
                    switchSTPUrl = f"https://api.meraki.com/api/v1/networks/{vlans['networkId']}/switch/stp"
                    switchSTPResponse = requests.get(headers=headers,url=switchSTPUrl).json()
                    MGMTvlan = True
                    rootSwitch = None
                    if vlans['id'] == switchResponse['vlan']: #confirms if switch settings utilize management Vlan properly
                        response += f'  {network['name']} "{vlans['name']}" Management Vlan properly configured on {switchResponse['vlan']} with subnet {vlans['subnet']}\n'
                    else: response += f'  {network['name']} Management Vlan: "{vlans['name']}" configured as vlan {vlans['id']} subnet {vlans['subnet']} but switch settings configured as Management vlan {switchResponse['vlan']}\n'
                    if switchSTPResponse["stpBridgePriority"][0]["stpPriority"] in (0, 4096, 8192):
                        rootSwitch = switchSTPResponse["stpBridgePriority"][0]['switches'][0]
                    else: response += f'    {network['name']} does not have a properly configured Meraki switch with a priority of 0, 4096, or 8192\n'
                    for switchDevice in switchDeviceResponse: #loops through switches to confirm if properly assigned to management Vlan and if switch is root
                        if network['id'] == switchDevice['networkId']:
                            is_mgmt_ip = vlans['subnet'].split('.')[:3] == switchDevice['lanIp'].split('.')[:3]
                            is_root = switchDevice['serial'] == rootSwitch
                            base = (f"    Switch:{switchDevice['name']} with Serial:{switchDevice['serial']} has valid IP:{switchDevice['lanIp']} {'on' if is_mgmt_ip else 'not on'} Management Vlan {vlans['id']}")
                            if is_root:
                                base += f" and is the Root with a priority of {switchSTPResponse['stpBridgePriority'][0]['stpPriority']}"
                            response += base + "\n"
            if not MGMTvlan: 
                response += f"  {network['name']} has no Management Vlan Configured\n"
        elif 'appliance' in network['productTypes']: 
            response += f"  {network['name']} has MX but no Meraki switches\n"
        elif 'switch' in network['productTypes']:
            response += f"  {network['name']} has Meraki switches but no MX\n"
        response += "\n"
    response += "\n\n\n"
    return response


def run_all_checks(org_list, output_filename="./meraki/results/mgmt_check_output.txt", max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(mgmtCheck, org, headers): org for org in org_list}
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
    run_all_checks(orgs[:4])