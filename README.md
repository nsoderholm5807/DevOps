# Proton - Meraki Management Scripts

This repository contains Python scripts for managing and auditing Meraki networks using the Meraki Dashboard API.

## Prerequisites

- Python 3.7 or higher
- `requests` library (install via `pip install requests`)
- `rich` library (install via `pip install rich`)
- A valid Meraki API key with appropriate permissions

## Setup

### 1. API Key Configuration

Create a file named `secret.py` in the `meraki/` folder with your Meraki API keys:

```python
# meraki/secret.py
devKey = "your_development_api_key_here"
prodKey = "your_production_api_key_here"
```

- Replace `your_development_api_key_here` and `your_production_api_key_here` with your actual Meraki API keys.
- The scripts use `prodKey` by default for production operations.

### 2. Generate Organizations List

Run the `generateOrg.py` script to fetch and generate the list of organizations:

```bash
python meraki/generateOrg.py
```

This will create or update `meraki/orgs.py` with the current list of organizations accessible via your API key.

## Usage

After setup, you can run the various scripts to perform audits and checks on your Meraki networks.

### Available Scripts

- **`generateOrg.py`**: Fetches and generates the organizations list in `orgs.py`.
- **`switchCheck.py`**: Checks switches configured for DHCP in each organization and network.
- **`mgmtVlanCheck.py`**: Performs management VLAN checks confirming if switch networks are probably configured with management VLANs and outputting any issues if discovered.

### Running Scripts

Most scripts can be run directly:

```bash
python meraki/switchCheck.py
```

Output files are typically generated in the root directory (e.g., `switch_check_output.txt`, `mgmt_check_output.txt`).

### Main Entry Point

You can also use `main.py` as the primary entry point if configured:

```bash
python main.py
```

## Examples

### Checking Switches for DHCP Configuration

```bash
python meraki/switchCheck.py
```

This will output results to `switch_check_output.txt`, listing organizations and networks with DHCP-configured switches.

### Generating Updated Organizations

```bash
python meraki/generateOrg.py
```

Run this periodically to refresh the organizations list if new organizations are added or removed.

## Notes

- Ensure your API key has the necessary permissions for the operations you're performing.
- Scripts use threading for concurrent API calls to improve performance.
- Output files are overwritten on each run; backup important results if needed.
- For production use, consider using the `prodKey` in `secret.py`.

## Troubleshooting

- If you encounter API rate limits, the scripts include basic error handling and retries.
- Check the console output for any error messages or API responses.
- Ensure `secret.py` is correctly formatted and contains valid API keys.
