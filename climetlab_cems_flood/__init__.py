from pathlib import Path
import datetime
from json import dump
from ._version import get_versions
from .api import sync_config

__version__ = get_versions()["version"]
del get_versions

CONFIG_PATH=Path.home() / ".climetlab" / "cems_config.json"

PRODUCTS = [
'cems-glofas-forecast',
'cems-glofas-historical',
'cems-glofas-reforecast',
'cems-glofas-seasonal-reforecast',
'cems-glofas-seasonal'
]

def placeholder():
        return {
        'cems-glofas-forecast':{'leadtime_step':24,'temporal_coverage':[2019, 2022]},
        'cems-glofas-historical':{'leadtime_step':24,'temporal_coverage':[1979, 2022]},
        'cems-glofas-reforecast':{'leadtime_step':24,'temporal_coverage':[1999, 2018]},
        'cems-glofas-seasonal-reforecast':{'leadtime_step':24,'temporal_coverage':[1981, 2022]},
        'cems-glofas-seasonal':{'leadtime_step':24,'temporal_coverage':[2019, 2022]}
        }

if not CONFIG_PATH.exists():
        CONFIG = placeholder()
        if not CONFIG_PATH.parent.exists(): 
                CONFIG_PATH.parent.mkdir()
        with open(CONFIG_PATH, "w") as f:
                dump(CONFIG, f)
else:
        try:
                CONFIG = sync_config(PRODUCTS, CONFIG_PATH)   
        except:
                CONFIG = placeholder()
      
print(f"Loading cems config: {CONFIG_PATH.absolute()}, last modified: {datetime.datetime.fromtimestamp(CONFIG_PATH.stat().st_mtime)}")