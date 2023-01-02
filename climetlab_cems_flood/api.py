from re import search
from requests import get
from json import dump, load

def api_get_cds_catalog(dataset=None):
    """Request product metadata. Fall back to cached metadata if request fails."""
    if dataset:  # request catalog product list
        URL = f"https://cds.climate.copernicus.eu/api/v2.ui/resources/{dataset}"
    else:
        URL = "https://cds.climate.copernicus.eu/api/v2.ui/resources/"
    with get(URL) as r:
        res = r.json()
    return res


def sync_config(products, config_path):
    with open(config_path, "r") as f:
        config = load(f)   
        update_all(products, config)
        
    with open(config_path, "w") as f: 
        dump(config, f)
        
    return config
 
   
def update_product(dataset, config):
    md = api_get_cds_catalog(dataset)

    sd = md.get('structured_data')
            
    tc = sd.get('temporalCoverage')
    lst = tc.split("/")
    start_year = int(search("([0-9]{4})", lst[0]).group())
    end_year = int(search("([0-9]{4})", lst[1]).group())
    config[dataset]["temporal_coverage"] = [start_year, end_year]
    

def update_all(products, config):
    for p in products:
        update_product(p, config)