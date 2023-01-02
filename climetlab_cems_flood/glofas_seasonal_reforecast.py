#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import climetlab as cml
from climetlab import Dataset


from .utils import (
    Parser,
    CommonMixin,
    preprocess_spatial_filter,
    build_multi_request,
    xarray_opendataset_config,
    store_request_param,
    months_num2str,
)


class GlofasSeasonalReforecast(Dataset, CommonMixin):

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

    def __init__(
        self,
        system_version,
        model,
        variable,
        temporal_filter,
        leadtime_hour,
        area=None,
        coords=None,
        split_on=None,
        threads=None,
        merger=None,
    ):

        store_request_param(self, ["param_area", "param_coords"], [area, coords])

        if threads is not None:
            cml.sources.SETTINGS.set("number-of-download-threads", threads)

        self.parser = Parser("cems-glofas-forecast")

        years, months, days = self.parser.temporal_filter(temporal_filter)

        leadtime_hour = self.parser.leadtime_hour(leadtime_hour, 24)

        months = months_num2str(months)

        self.request = {
            "system_version": system_version,
            "hydrological_model": model,
            "variable": variable,
            "hyear": years,
            "hmonth": months,
            "leadtime_hour": leadtime_hour,
            "format": "grib",
        }

        self._sf_ids = preprocess_spatial_filter(self.request, area, coords)

        if split_on is not None:
            sources, output_names = build_multi_request(
                self.request,
                split_on,
                self._sf_ids,
                dataset="cems-glofas-seasonal-reforecast",
            )
            self.output_names = output_names
            self.source = cml.load_source("multi", sources, merger=merger)

        else:
            self.output_names = None
            self.source = cml.load_source(
                "cds", "cems-glofas-seasonal-reforecast", **self.request
            )

    def to_xarray(self):
        return xarray_opendataset_config(self.source, self.name)
