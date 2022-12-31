#!/usr/bin/env python3
from __future__ import annotations

import climetlab as cml
from climetlab import Dataset

from .utils import (
    Parser,
    CommonMixin,
    months_num2str,
    preprocess_spatial_filter,
    build_multi_request,
    xarray_opendataset_config,
    store_request_param,
)


class GlofasHistorical(Dataset, CommonMixin):

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

    def __init__(
        self,
        system_version,
        product_type,
        model,
        variable,
        temporal_filter,
        area=None,
        coords=None,
        split_on=None,
        threads=None,
        merger=None,
    ):

        store_request_param(self, ["param_area", "param_coords"], [area, coords])

        if threads is not None:
            cml.sources.SETTINGS.set("number-of-download-threads", threads)

        self.parser = Parser("cems-glofas-historical")

        years, months, days = self.parser.temporal_filter(temporal_filter)

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
        }

        self._sf_ids = preprocess_spatial_filter(self.request, area, coords)

        if split_on is not None:
            sources, file_output_names = build_multi_request(
                self.request, split_on, self._sf_ids, dataset="cems-glofas-historical"
            )
            self.output_names = file_output_names
            self.source = cml.load_source("multi", sources, merger=merger)
        else:
            self.output_names = None
            self.source = cml.load_source(
                "cds", "cems-glofas-historical", **self.request
            )

    def to_xarray(self):
        return xarray_opendataset_config(self.source, self.name)
