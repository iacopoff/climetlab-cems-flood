from re import fullmatch
from requests import get
from datetime import datetime, timedelta
from functools import partial
from itertools import product, chain
from typing import List, Dict
from copy import deepcopy
from pathlib import Path
from importlib import resources
from collections.abc import Iterable

from climetlab import load_source
from . import CONFIG

DEFAULT_KEY_MAPPING = {
    "leadtime_hour": "lh",
    "river_discharge_in_the_last_24_hours": "rivo",
    "control_forecast": "cf",
    "snow_melt_water_equivalent": "swe",
}


class NotSupportedQuery(Exception):
    pass


class StringNotValidError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def ensure_list(l):
    if isinstance(l, list):
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
    return [str(i) if i >= 10 else f"0{str(i)}" for i in l0]


def branch(x, dc_map):
    if (
        fullmatch("((\d{4} \d{2} \d{2})(\/|$))+", x) and len(x) > 10
    ):  # not contiguous sequence list of dates
        # this query need to be handled differently as one request per date should be sent
        raise NotSupportedQuery
    elif (
        fullmatch("((\d{4} \d{2} \d{2})(-|$))+", x) and len(x) > 10
    ):  # contiguous sequence of dates
        # this query need to be handled differently as the CDS does not works with from-to dates but ranges of years, months, days
        raise NotSupportedQuery
    else:
        out = split(x, dc_map)
    return out


def split(string: str, dc_map):

    date_components = string.split(" ")  # %Y %m %d

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
                start, end = list(map(int, chunk.split("-")))
                remainder = end % leadtime_step == 0
                ret.extend(list(map(str, range(start, end + remainder, leadtime_step))))
            else:
                ret.append(chunk)

        return ret

    def temporal_filter(self, string, **kwargs) -> List:

        temporal_coverage = CONFIG.get(self.product).get("temporal_coverage")
        assert isinstance(temporal_coverage, list)
        start_year = temporal_coverage[0]
        end_year = temporal_coverage[-1]

        self.range_year = range_year = [str(y) for y in range(start_year, end_year + 1)]

        dc_map = {
            0: range_year,  # year
            1: [d for d in range(1, 13)],
            2: [d for d in range(1, 32)],
        }

        years, months, days = branch(string, dc_map)

        # check request is within temporal coverage
        if int(years[0]) < start_year or int(years[-1]) > end_year:
            raise ValueError(
                f"Time filter is not within temporal coverage {start_year}-{end_year}"
            )

        return years, months, days


def months_num2str(months: List[str]):
    mapping = {
        "01": "january",
        "02": "february",
        "03": "march",
        "04": "april",
        "05": "may",
        "06": "june",
        "07": "july",
        "08": "august",
        "09": "september",
        "10": "october",
        "11": "november",
        "12": "december",
    }
    return [mapping.get(m) for m in months if mapping.get(m)]


def ismulty(x: list | tuple | str | dict):
    cond1 = all([isinstance(i, Iterable) and not isinstance(i, str) for i in x])
    cond2 = len(x) > 1
    return cond1 and cond2


def preprocess_spatial_filter(request, area: List[Dict], coords: List[Dict]) -> List[str]:
    ids = [] 
    cds_area: List[List] = []
    if coords is not None:
        if area is not None:
            raise ValueError("area AND coords are not allowed together")
        if ismulty(coords):
            for coord in coords:
                lat = coord.get('lat')
                lon = coord.get('lon')
                cds_area.append([lat, lon, lat, lon])  # N/W/S/E
                ids.append(coord.get('name'))
        else:
            lat = coords[0].get('lat')
            lon = coords[0].get('lon')
            cds_area = [lat, lon, lat, lon]   # N/W/S/E
            ids.append(coords[0].get('name'))
    if area is not None:
        if coords is not None:
            raise ValueError("area AND coords are not allowed together")
        if ismulty(area):
            for a in area:
                ids.append(a.get('name'))
                cds_area.append(a.get('area'))
        else:
            cds_area = area[0].get('area')
            ids.append(area[0].get('name'))
    
    if isinstance(cds_area, list):
        request.update({"area": cds_area})
    elif type(area).__name__ == "GeoDataFrame" or type(area).__name__ == "GeoSeries":
        W, S, E, N = area.unary_union.bounds  # (minx, miny, maxx, maxy)
        bounds = [N, W, S, E]
        request.update({"area": bounds})
    return ids


class ReprMixin:
    def _set_paths(self, output_folder, output_name_prefix):
        self.output_folder = Path(output_folder)
        self.output_name_prefix = output_name_prefix
        self.output_name = "_".join([self.output_name_prefix, self.name])
        self.output_path = None

        if self.output_names is None:
            self.output_path = [self.output_folder / self.output_name]
        else:
            self.output_path = []
            for fn in self.output_names:
                file_name = "_".join([self.output_name, fn])
                self.output_path.append(self.output_folder / file_name)

    def to_netcdf(
        self, output_folder, output_name_prefix
    ):  # all individual save or merge everything and then save

        self._set_paths(output_folder, output_name_prefix)

        paths = []
        if len(self.output_path) < 2:
            ds = self.to_xarray()
            p = self.output_path[0].with_suffix(".nc")
            paths.append(p)
            if not p.exists():
                ds.to_netcdf(p)
        else:
            for i, src in enumerate(self.source.indexes): # self.source.sources
                ds = src.to_xarray(backend_kwargs={'time_dims': ['time']}).isel(surface=0, step=0, drop=True).drop_vars(["valid_time"])
                p = self.output_path[i].with_suffix(".nc")
                stem = self.output_path[i].stem.split("_")[-1]
                ds = ds.expand_dims({"station": [stem]})
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

        return (
            ret
            + f"""<table class="climetlab"><tr><td><b>Request</b></td><td><ul>{li}</ul></td></tr></table>"""
        )


def validate_params(func):
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret

    return inner


def chunking(param, requested_param_values: List[List], chunk_size: int) -> list[list[str]]:
    
    if param == 'area' or param == 'coords':
        if ismulty(requested_param_values):
            chunks = [
                requested_param_values[i : i + chunk_size]
                for i in range(0, len(requested_param_values), chunk_size)
            ]
            chunks = list(chain(*chunks))
        else:
            chunks = [requested_param_values]
    else:
        chunks = [
            requested_param_values[i : i + chunk_size]
            for i in range(0, len(requested_param_values), chunk_size)
        ]
    return chunks


def generate_output_name(subreq, subreq_params, sf_id, key_mapping) -> str:
    """Generate an output name for every subrequest. To be used by conversion methods. 
    
    ex:
    output_name = <param1>-<values1>_<param2>-<values2> ...
    Parameters
    ----------
    subreq : _type_
        _description_
    subreq_params : _type_
        _description_
    sf_id : _type_
        _description_
    key_mapping : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    mapping = DEFAULT_KEY_MAPPING | key_mapping
    strings = []
    for values, param in zip(subreq, subreq_params):
        if param == "area":
            val_name = sf_id
        elif len(values) >= 2:
            val_name = f"{values[0]}-{values[-1]}"
        else:
            val_name = values[0]
        param = mapping.get(param, param)
        val_name = mapping.get(val_name, val_name)
        strings.append("-".join([param, val_name]))
    return "_".join(strings)


def validate_spliton(split_on):
    r_split_on, param_names = [], []
    for subreq in split_on:
        if isinstance(subreq, tuple):
            r_split_on.append(subreq)
            param_names.append(subreq[0])
        else:
            r_split_on.append((subreq, 1))
            param_names.append(subreq)
    return r_split_on, param_names


def build_multi_request(
    request: dict, split_on: List[tuple | str], sf_ids: List[str], dataset: str, key_mapping={}
):
    """
    Takes a request and splits it in indepedent sub-requests defined by `split_on`.

    Parameters
    ----------
    request : dict
        _description_
    split_on : list
        Indicates how to split the request based on parameters.
        User should define 1) parameter and 2) N. items in each sub-request.
        Ex:
            ("month", 2) indicates that 2-months sub-requests are submitted.
        When no items are indicated 1-sized sub-requests are submitted.
    dataset : str
        Name of the dataset
    key_mapping : dict, optional
        _description_, by default {}

    Returns
    -------
    _type_
        _description_
    """

    split_on, subreq_params = validate_spliton(split_on)

    # The request to the CDS always requires an 'area' keyword
    if "coords" in subreq_params:
        subreq_params[subreq_params.index("coords")] = "area"
        split_on = [("area", t[1]) if "coords" in t else t for t in split_on]

    if (
        "area" not in subreq_params
        and "area" in request.keys()
        and ismulty(request["area"])
    ):
        raise ValueError(
            "If requesting to split by multiple coords or areas, you should add 'area' or 'coords' to split_on"
        )
    sources, file_output_names = [], []
    subrequests = list(
        product(*[chunking(subreq[0], request[subreq[0]], subreq[1]) for subreq in split_on])
    )
    len_subreqs = len(subrequests) // len(sf_ids)
    sf_ids = list(chain(*[[i]*len_subreqs for i in sf_ids]))
    
    for i, subreq in enumerate(subrequests):
        new_req = deepcopy(request)
        subreq_dict = {k: v for k, v in zip(subreq_params, subreq)}
        new_req.update(subreq_dict)
        sources.append(partial(load_source, "cds", dataset, new_req))
        if len(sf_ids) > 1: 
            file_output_names.append(generate_output_name(subreq, subreq_params, sf_ids[i] , key_mapping))
        else:
            file_output_names.append(generate_output_name(subreq, subreq_params, sf_ids[0] , key_mapping))
        
    return sources, file_output_names


def get_po_basin():
    import geopandas as gpd

    with resources.path("climetlab_cems_flood.data", "po_basin.geojson") as f:
        data_file_path = f
    return gpd.read_file(data_file_path)


def show_request_for_parameter(product, key, value, return_output=False) -> List:
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
    """Request product metadata. Fall back to cached metadata if request fails."""
    if dataset:  # request catalog product list
        URL = f"https://cds.climate.copernicus.eu/api/v2.ui/resources/{dataset}"
    else:
        URL = "https://cds.climate.copernicus.eu/api/v2.ui/resources/"
    with get(URL) as r:
        res = r.json()

    ex = res["structured_data"]["temporalCoverage"]
    return ex
