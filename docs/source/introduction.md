
# Introduction

The `climetlab-cems-flood` plugin uses the CliMetLab's machinery to programmaticaly download data from the **Climate Data Store (CDS)**.

```{warning}
For accessing the CDS, it is necessary to subscribe and configure the [CDS API key](https://cds.climate.copernicus.eu/api-how-to) on your local local machine.
```


```python
import climetlab as cml

dataset = cml.load_dataset(
            'cems-glofas-seasonal',
            model='lisflood',
            system_version='operational',
            temporal_filter= '2022 01 01',
            leadtime_hour = '24-72',
            variable="river_discharge_in_the_last_24_hours"
)

ds = dataset.to_xarray()

ds
(<xarray.Dataset>
 Dimensions:                  (realization: 51, forecast_reference_time: 1,
                               leadtime: 3, lat: 1500, lon: 3600)
 Coordinates:
   * realization              (realization) int64 0 1 2 3 4 5 ... 46 47 48 49 50
   * forecast_reference_time  (forecast_reference_time) datetime64[ns] 2022-01-01
   * leadtime                 (leadtime) timedelta64[ns] 1 days 2 days 3 days
   * lat                      (lat) float64 -59.95 -59.85 -59.75 ... 89.85 89.95
   * lon                      (lon) float64 -179.9 -179.8 -179.8 ... 179.8 540.0
     time                     (forecast_reference_time, leadtime) datetime64[ns] ...
 Data variables:
     dis24                    (realization, forecast_reference_time, leadtime, lat, lon) float32 ...
 Attributes:
     GRIB_edition:            2
     GRIB_centre:             ecmf
     GRIB_centreDescription:  European Centre for Medium-Range Weather Forecasts
     GRIB_subCentre:          0
     Conventions:             CF-1.7
     institution:             European Centre for Medium-Range Weather Forecasts
     history:                 2023-01-02T10:51 GRIB to CDM+CF via cfgrib-0.9.1...,)
```
