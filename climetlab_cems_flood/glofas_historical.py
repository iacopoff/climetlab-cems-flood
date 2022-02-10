#!/usr/bin/env python3
from __future__ import annotations

import climetlab as cml
from climetlab import Dataset

from .utils import Parser, months_num2str

from functools import partial


def ensure_list(x):
    if isinstance(x, list):
        return x
    else:
        return [x]

class GlofasHistorical(Dataset):
    name = None
    home_page = "https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-historical?tab=overview"
    licence = "https://cds.climate.copernicus.eu/api/v2/terms/static/cems-floods.pdf"
    documentation = "https://cds.climate.copernicus.eu/cdsapp#!/dataset/cems-glofas-historical?tab=doc"
    citation = "-"
    request = "-"


    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://github.com/ecmwf-lab/climetlab_cems_flood/LICENSE"
        "If you do not agree with such terms, do not download the data. "
    )

    dataset = None

    temporal_range = [1979,2021]

    def __init__(self, system_version, product_type, model, variable, period, area = None, lat = None, lon = None, split_on =None):
        
        self.parser = Parser(self.temporal_range)

        years, months, days = self.parser.period(period)

        months = months_num2str(months)

        if lat is not None and lon is not None:
            area = []
            lat, lon = list(map(ensure_list,[lat,lon]))
            for la,lo in zip(lat,lon):
                area.extend([la,lo,la,lo]) # N/W/S/E

            

        self.request = {
            "system_version": system_version,
            "hydrological_model": model,
            "product_type": product_type,
            "variable": variable,
            "hyear": years,
            "hmonth": months,
            "hday": days,
            "format": "grib",
            #"split_on": "area"s
        }



        if area:
            self.request.update({"area":area})

       
        self.source = cml.load_source("cds", "cems-glofas-historical", **self.request)


    def to_xarray(self):
        return self.source.to_xarray(backend_kwargs={'time_dims':['time']}).isel(surface=0, step=0, drop=True).drop_vars(["valid_time"])


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