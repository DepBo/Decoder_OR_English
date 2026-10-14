"""
experiments/technology_mapping/download_libraries.py
----------------------------------------------------
Downloads standard-cell Liberty (.lib) libraries:
1. Nangate45 Open Cell Library (NangateOpenCellLibrary_typical.lib, 45nm, Si2 license)
2. SkyWater SKY130 HD (sky130_fd_sc_hd__tt_025C_1v80.lib, 130nm, Apache 2.0)
"""

import urllib.request
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parent / "libraries"
LIB_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "NangateOpenCellLibrary_typical.lib": "https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib",
    "sky130_fd_sc_hd__tt_025C_1v80.lib": "https://raw.githubusercontent.com/efabless/skywater-pdk-libs-sky130_fd_sc_hd/master/timing/sky130_fd_sc_hd__tt_025C_1v80.lib",
}

for name, url in URLS.items():
    dest = LIB_DIR / name
    if not dest.exists() or dest.stat().st_size < 1000:
        print(f"Downloading {name} from {url}...")
        urllib.request.urlretrieve(url, dest)
        print(f"  Downloaded {name}: {dest.stat().st_size:,} bytes")
    else:
        print(f"  Existing {name}: {dest.stat().st_size:,} bytes")

print("Library download check complete.")
