
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

CONFIG = {
        'glofas-forecast':{'leadtime_step':24,'temporal_coverage':[2019, 2022]},
        'glofas-historical':{'leadtime_step':24,'temporal_coverage':[1979, 2022]},
        'glofas-reforecast':{'leadtime_step':24,'temporal_coverage':[1999, 2018]},
        'glofas-seasonal-reforecast':{'leadtime_step':24,'temporal_coverage':[1981, 2022]},
        'glofas-seasonal':{'leadtime_step':24,'temporal_coverage':[2019,2022]}
}