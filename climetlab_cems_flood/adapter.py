from typing import Dict, List, Union
from pathlib import Path
import climetlab as cml
import rechunker as rc
"""
The adapter should configure where, what and how the data should be saved.
The scopes are:
1. Save and cache files in a non default directory with user selected names
2. On top of (1) prepare data for the viewer (slice vs series orientation)
"""



class Adapter:

    def __init__(self, dataset: cml.Dataset, output_folder: str, output_name_prefix: str, output_format: str, key_mapping: Dict[str, str] = None):
        self.dataset = dataset
        self.out_folder = output_folder
        self.out_name_prefix = output_name_prefix
        self.output_format = output_format



    def to_netcdf(): # all individual save or merge everything and then save
        ds = self.dataset.to_xarray()
        ds.to_netcdf()

    def to_zarr(rechunk: bool = False, target_chunks: Dict[str, Union[Dict[str, int], None]] = {}, max_mem: str = '2M', temp_store = 'temp.zarr'):
        ret = self.dataset.to_zarr()

        if rechunk:
            rc.rechunk(source_group, target_chunks, max_mem, target_store, temp_store=temp_store)
            # remove temp store
            # replace source group with target store



