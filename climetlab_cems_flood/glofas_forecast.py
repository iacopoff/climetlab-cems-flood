#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import climetlab as cml
from climetlab import Dataset
import cf2cdm


from .utils import (
    Parser,
    ReprMixin,
    months_num2str,
    handle_cropping_area,
    ensure_list,
    build_multi_request
)




class GlofasForecast(Dataset, ReprMixin):
    name = None
    home_page = "-"
    licence = "-"
    documentation = "-"
    citation = "-"
    request = "-"

    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://github.com/ecmwf-lab/climetlab_cems_flood/LICENSE"
        "If you do not agree with such terms, do not download the data. "
    )

    temporal_range = [2019, date.today().year]

    def __init__(
        self,
        system_version,
        product_type,
        model,
        variable,
        period,
        leadtime_hour,
        area=None,
        lat=None,
        lon=None,
        split_on=None,
        threads=None,
        merger=None
    ):

        if threads is not None:
            cml.sources.SETTINGS.set("number-of-download-threads", threads)

        self.parser = Parser(self.temporal_range)

        years, months, days = self.parser.period(period)

        leadtime_hour = self.parser.leadtime(leadtime_hour, 24)

        self.request = {
            "system_version": system_version,
            "hydrological_model": model,
            "product_type": product_type,
            "variable": variable,
            "year": years,
            "month": months,
            "day": days,
            "leadtime_hour": leadtime_hour,
            "format": "grib",
        }

        handle_cropping_area(self.request, area, lat, lon)

        if split_on is not None:
            sources, output_names = build_multi_request(self.request, split_on, dataset ='cems-glofas-forecast')
            self.output_names = output_names
            self.source = cml.load_source("multi", sources, merger=merger)
            
        else:
            self.output_names = None
            self.source = cml.load_source("cds", "cems-glofas-forecast", **self.request)
            
        #import pdb;pdb.set_trace()

        # Save to netcdf or zarr



    def to_xarray(self):
        ds = self.source.to_xarray().isel(surface=0, drop=True)
        return cf2cdm.translate_coords(ds, cf2cdm.CDS)


    # def to_netcdf(self):
    #     pass

    # def to_zarr(self):
    #     pass