
# Introduction

Currently the plugin allows only download of GloFAS data. The aim is to add EFAS as well in the near future.

In order to download data from the CDS you have to subscribe and configure the [CDS API key](https://cds.climate.copernicus.eu/api-how-to) on you local machine.

Basically this plugin is a wrapper around the [CDS API](https://cds.climate.copernicus.eu): the parameters to be passed to the `load_dataset` method are processed and sent to the `cdsapi.Client().retrieve({...})` request.

```python
import climetlab as cml

ds = cml.load_dataset(
            'cems-flood-glofas-seasonal',
            model='lisflood',
            system_version='operational',
            period= '20220101',
            leadtime_hour = '24-3600',
            variable="river_discharge_in_the_last_24_hours",
)
```
