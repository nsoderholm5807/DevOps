# Proton - Meraki Management Scripts

This repository contains Python scripts for managing and auditing Meraki networks using the Meraki Dashboard API.

## Prerequisites

- Python 3.13 or higher
- `requests` library
- `rich` library
- A valid Meraki API key with appropriate permissions

## Setup

### 1. API Key Configuration

This project loads Meraki API keys from environment variables via `meraki/settings/secret.py`.
Create a local file named `meraki/settings.env` with your values:

```env
MERAKI_ENV=prod
MERAKI_DEV_KEY=your_dev_api_key
MERAKI_PROD_KEY=your_prod_api_key
```

- Replace `your_dev_api_key` and `your_prod_api_key` with your actual Meraki API keys.
- `MERAKI_ENV` is optional and can be set to `dev` or `prod`.
- `meraki/settings/secret.py` loads `meraki/settings.env`.

### 2. Current File Structure

Key files and folders:

- `meraki/`
  - `monitoring/`
    - `mgmtVlanCheck.py`
    - `switchCheck.py`
  - `settings/`
    - `generateOrg.py`
    - `secret.py`
    - `settings.env`
  - `results/`
- `pyproject.toml`
- `README.md`

### 3. Generate Organizations List

Run the generator from the project root:

```bash
cd /path/to/project-root
.venv/bin/python -m meraki.settings.generateOrg
```

This creates or updates `meraki/orgs.py` with the current list of organizations accessible via your API key.

## Usage

After setup, run the available audit scripts from the repository root.

### Available Scripts

- `meraki/settings/generateOrg.py`: fetches organizations and writes `meraki/orgs.py`
- `meraki/monitoring/switchCheck.py`: checks switches configured for DHCP
- `meraki/monitoring/mgmtVlanCheck.py`: audits management VLAN configuration for Meraki networks

### Running Scripts

From the repository root, run scripts as modules:

```bash
cd /path/to/project-root
.venv/bin/python -m meraki.monitoring.switchCheck
.venv/bin/python -m meraki.monitoring.mgmtVlanCheck
```

Or run the organization generator directly:

```bash
cd /path/to/project-root
.venv/bin/python -m meraki.settings.generateOrg
```

### Output Files

- `meraki/results/mgmt_check_output.txt` by default for `mgmtVlanCheck.py`
- `switch_check_output.txt` by default for `switchCheck.py`

## Notes

- Scripts should be run from the repository root so package imports resolve cleanly.
- Output files are overwritten on each run.
- `meraki/settings/secret.py` must load valid API keys before scripts can run.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'meraki'`, run from the project root and use `python -m ...`.
- Validate `meraki/settings.env` values and confirm `MERAKI_DEV_KEY` / `MERAKI_PROD_KEY` are set.
- If API calls fail, check the API key permissions and rate-limit responses.
