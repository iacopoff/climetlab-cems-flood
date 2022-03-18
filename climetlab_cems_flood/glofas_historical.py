#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import climetlab as cml
from climetlab import Dataset

from .utils import Parser, ReprMixin, months_num2str, handle_cropping_area

from functools import partial


class GlofasHistorical(Dataset, ReprMixin):
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

    temporal_range = [1979, date.today().year]

    def __init__(self, system_version, product_type, model, variable, period, area = None, lat = None, lon = None, split_on =None): 
        
        self.parser = Parser(self.temporal_range)

        years, months, days = self.parser.period(period)

        months = months_num2str(months)
            
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

        handle_cropping_area(self.request, area, lat, lon)
       
        self.source = cml.load_source("cds", "cems-glofas-historical", **self.request)


    def to_xarray(self):
        return self.source.to_xarray(backend_kwargs={'time_dims':['time']}).isel(surface=0, step=0, drop=True).drop_vars(["valid_time"])


