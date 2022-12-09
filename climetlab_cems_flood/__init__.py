
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

CONFIG = {
        'glofas-forecast':{'leadtime_step':24,'temporal_coverage':[2019]},
        'glofas-historical':{'leadtime_step':24,'temporal_coverage':[1979]},
        'glofas-reforecast':{'leadtime_step':24,'temporal_coverage':[1991, 2018]},
        'glofas-seasonal-reforecast':{'leadtime_step':24,'temporal_coverage':[1981, 2020]},
        'glofas-seasonal':{'leadtime_step':24,'temporal_coverage':[2020]}
}