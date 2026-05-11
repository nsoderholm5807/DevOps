from pathlib import Path
from dotenv import load_dotenv
import os

base_dir = Path(__file__).resolve().parent
# load_dotenv(base_dir / ".env")
load_dotenv(base_dir / "settings.env")

env = os.getenv("MERAKI_ENV")
devKey = os.getenv("MERAKI_DEV_KEY")
prodKey = os.getenv("MERAKI_PROD_KEY")

if not devKey or not prodKey:
    raise RuntimeError("MERAKI_DEV_KEY and MERAKI_PROD_KEY must be set")