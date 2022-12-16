from datetime import datetime, timedelta, date
from functools import partial
from itertools import product
import typing as T
from typing import List
import re
from climetlab import load_source
from copy import deepcopy
from pathlib import Path
from importlib import resources

import requests
from . import CONFIG

class NotSupportedQuery(Exception):
    pass

M = ["%02d"%d for  d in range(1,13)]
D = ["%02d"%d for  d in range(1,32)]
DEFAULT_KEY_MAPPING = {"leadtime_hour":"lh", 
                        "river_discharge_in_the_last_24_hours":"rivo",
                        'control_forecast':'cf',    
                        'snow_melt_water_equivalent':'swe'}

class StringNotValidError(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def ensure_list(l):
    if isinstance(l,list):
        return l
    else:
        return [l]

def parser_time_index(start=[2019, 1, 1], end=[2019, 12, 31]):

    start, end = datetime(*start), datetime(*end)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    index = [
        list(map(str.lower, d.strftime("%B-%d").split("-")))
        for d in days
        if d.weekday() in [0, 3]
    ]

    return index

def ensure_list_of_str(l):
    l0 = [int(i) for i in l]
    return [str(i) if i >= 10 else f"0{str(i)}" for i in l0 ]



def branch(x, dc_map):
    if re.fullmatch("((\d{4} \d{2} \d{2})(\/|$))+", x) and len(x)> 10: # not contiguous sequence list of dates
        # this query need to be handled differently as one request per date should be sent
        raise NotSupportedQuery
    elif re.fullmatch("((\d{4} \d{2} \d{2})(-|$))+", x) and len(x)> 10: # contiguous sequence of dates
        # this query need to be handled differently as the CDS does not works with from-to dates but ranges of years, months, days
        raise NotSupportedQuery
    else:
        out = split(x, dc_map)
    return out 
def split(string: str, dc_map):

    date_components = string.split(" ") # %Y %m %d

    out = []
    for i, dc in enumerate(date_components):
        if "-" in dc:
            dc_from, dc_to = [*map(int, dc.split("-"))]
            out.insert(i, ensure_list_of_str([*range(dc_from, dc_to + 1)]))
        elif "/" in dc:
            out.insert(i, ensure_list_of_str(dc.split("/")))
        elif "*" in dc:
            out.insert(i, ensure_list_of_str(dc_map[i]))
        else:  # not a list
            out.insert(i, ensure_list(dc))

    return out

          
class Parser:

    def __init__(self, product):
        self.product = product
    
    @staticmethod
    def leadtime_hour(value: str, leadtime_step: int, **kwargs) -> List:
        """Default to closed interval

        Parameters
        ----------
        value : str
            _description_
        leadtime_step : int
            _description_

        Returns
        -------
        List
            _description_
        """
        ret = []
        s = value.split("/")
        for chunk in s:
            if "-" in chunk:
                start, end = list(map(int,chunk.split("-")))
                remainder = end % leadtime_step == 0
                ret.extend(list(map(str, range(start, end + remainder, leadtime_step))))
            else:
                ret.append(chunk)

        return ret

    def temporal_filter(self, string, **kwargs) -> List:
        
        temporal_coverage = CONFIG.get(self.product).get('temporal_coverage') 
        assert isinstance(temporal_coverage, list)
        start_year = temporal_coverage[0]
        end_year = temporal_coverage[-1]
        
        self.range_year = range_year = [str(y) for y in range(start_year,end_year + 1)]

        dc_map = {
            0: range_year, # year
            1: [d for  d in range(1,13)],
            2: [d for  d in range(1,32)],
        }  

        
        years,months,days = branch(string, dc_map)
        
        # check request is within temporal coverage
        if int(years[0]) < start_year or int(years[-1]) > end_year:
            raise ValueError(f'Time filter is not within temporal coverage {start_year}-{end_year}')
        
        return years, months, days



def _validate(string):
    if ("*" in string and "-" in string) or ("*" in string and "/" in string):
        raise StringNotValidError(string," '*' and '-' or '*' and '/' are not allowed in the same string")
    else:
        pass

def months_num2str(months: T.List[str]):
    mapping = {"01":"january","02":"february","03":"march","04":"april","05":"may",
               "06":"june","07":"july","08":"august","09":"september","10":"october",
              "11":"november","12":"december"}
    return [mapping.get(m) for m in months if mapping.get(m)]



def unpack(string):
    try:
        string.split("-")
        start, end = string.split("-")
        if len(start) <= 2:
            return ["%02d"%d for d in range(int(start),int(end)+1)]
        elif len(start) > 2:
            return [str(d) for d in range(int(start),int(end)+1)] 
    except:
        return string
    


def handle_cropping_area(request, area, lat, lon):

    if lat is not None and lon is not None:
        if area is not None:
            raise ValueError("Can't have ('lat' or 'lon') and 'area'")
        # Compute area from coordinates (MARS client)
        area = []
        lat, lon = list(map(ensure_list,[lat,lon]))
        for la,lo in zip(lat,lon):
            area.extend([la,lo,la,lo]) # N/W/S/E
    print(area)
    if isinstance(area, list):  
        request.update({"area":area})
    elif type(area).__name__ == 'GeoDataFrame' or type(area).__name__ == 'GeoSeries':
        W,S,E,N = area.unary_union.bounds # (minx, miny, maxx, maxy)
        bounds = [N,W,S,E]
        request.update({"area":bounds})


class ReprMixin:
    
    def _set_paths(self, output_folder, output_name_prefix):
        self.output_folder = Path(output_folder)
        self.output_name_prefix = output_name_prefix
        self.output_name = "_".join([self.output_name_prefix,self.name])
        self.output_path = None
        

        if self.output_names is None:
            self.output_path = [self.output_folder / self.output_name]
        else:
            self.output_path = []
            for fn in self.output_names:
                file_name = "_".join([self.output_name, fn])
                self.output_path.append(self.output_folder / file_name)
                
    def to_netcdf(self, output_folder, output_name_prefix): # all individual save or merge everything and then save
        
        self._set_paths(output_folder, output_name_prefix)
        
        paths = []    
        if len(self.output_path) < 2:
            ds = self.to_xarray()
            p = self.output_path[0].with_suffix('.nc')
            paths.append(p)
            if not p.exists():
                ds.to_netcdf(p)
        else:
            for i,src in enumerate(self.source.sources):
                ds = src.to_xarray()
                p = self.output_path[i].with_suffix('.nc')
                paths.append(p)
                if not p.exists():
                    ds.to_netcdf(p)
                    
                             
    def _repr_html_(self):
        ret = super()._repr_html_()
    
        style = """
            <style>table.climetlab td {
            vertical-align: top;
            text-align: left !important;}
        </style>"""      
        
        li = ""
        for key in self.request:
            li += f"<li> <b>{key}: </b> {self.request[key]} </li>".format()
            
        return ret + f"""<table class="climetlab"><tr><td><b>Request</b></td><td><ul>{li}</ul></td></tr></table>"""




def validate_params(func):
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret 

    return inner


def chunking(requested_param_values: tuple[str], chunk_size: int) -> list[list[str]]:
    """
    
    """
    if chunk_size is None:
        return [ensure_list(requested_param_values)]
    return [requested_param_values[i:i+chunk_size] for i in range(0, len(requested_param_values), chunk_size)]



def translate(chunk: tuple[list[str]], param_spliton_names, key_mapping):
    """
    the weird chunk is the one on the area parameter as it is a list
    of list with integers.
    """
    mapping = DEFAULT_KEY_MAPPING | key_mapping 
    strings = [] 
    for param_values,param_name in zip(chunk, param_spliton_names):
        if param_name == 'area':
            p = list(map(str,param_values[0])) # TO DO: this whould be ensured at a higher level, when validating the user's request dictionary 
            val_name = "-".join(p)
        elif len(param_values) < 2:
            val_name = param_values[0]
        else:
            val_name = f"{param_values[0]}-{param_values[-1]}"
        param_name = mapping.get(param_name, param_name)
        val_name = mapping.get(val_name, val_name)
        strings.append("-".join([param_name, val_name]))
    return "_".join(strings)


def build_multi_request(request, split_on, dataset, key_mapping= {}):
    """
    split_on is a list of tuples. Each tuple contains the parameter name by which a request should be split and 
    and an indication of the number of element in each chunk.
    When the number of element in a chunk is missing it is assumed that the parameter is split in 1-sized chunks.
    """
    split_on: list[tuple] = [i if isinstance(i, tuple) else (i, 1) for i in split_on]
    param_spliton_names: list[str] = [i[0] if isinstance(i, tuple) else i for i in split_on]
    sources = []
    output_names = []
    chunks: list[tuple[list[str]]] = list(
        product(*[chunking(request[tup[0]], tup[1]) for tup in split_on])
    )

    for chunk in chunks:
        output_name = translate(chunk, param_spliton_names, key_mapping)
        d = {k[0]: v for k, v in zip(split_on, chunk)}
        r = deepcopy(request)
        r.update(d)
        sources.append(
            partial(load_source, "cds", dataset, r)
        )
        output_names.append(output_name)
    return sources, output_names



def get_po_basin():
    import geopandas as gpd
    with resources.path("climetlab_cems_flood.data", "po_basin.geojson") as f:
        data_file_path = f
    return gpd.read_file(data_file_path)



def show_request_for_parameter(product, key, value, return_output = False) -> List:    
    kwargs = CONFIG.get(product, False)
    if kwargs is None:
        raise f"Product not in list of supported products. \n Supported products are: {CONFIG.keys()}"
    try:    
        p = Parser(product)
        method = getattr(p, key)
        years, months, days = method(value, **kwargs)
    except AttributeError:
        raise AttributeError(f'Parameter "{key}" does not generate a valid request')
    print(f"years: {years}")
    print(f"months: {months}")
    print(f"days: {days}")
    if return_output:
        return years, months, days



def api_get_cds_catalog(dataset=None):
    """Request product metadata. Fall back to cached metadata if request fails. 
    """
    if dataset: #request catalog product list
        URL = f'https://cds.climate.copernicus.eu/api/v2.ui/resources/{dataset}'
    else:
        URL = 'https://cds.climate.copernicus.eu/api/v2.ui/resources/'
    with requests.get(URL) as r:
        res = r.json()
        
    ex = res['structured_data']['temporalCoverage']
    return ex