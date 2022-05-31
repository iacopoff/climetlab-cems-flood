
# Introduction

...WIP...

If you want to download GloFAS data, this is the right tool.

The `climetlab-cems-flood` plugin uses the CliMetLab's machinery and its conceptual framework made of [Datasets](https://climetlab.readthedocs.io/en/latest/guide/datasets.html) and [Data sources](https://climetlab.readthedocs.io/en/latest/guide/sources.html) to programmaticaly download data from the **Climate Data Store (CDS)**.

```{warning}
For accessing the CDS, it is necessary to subscribe and configure the [CDS API key](https://cds.climate.copernicus.eu/api-how-to) on your local local machine.
```



```python
import climetlab as cml

dataset = cml.load_dataset(
            'cems-flood-glofas-seasonal',
            model='lisflood',
            system_version='operational',
            period= '20220101',
            leadtime_hour = '24-3600',
            variable="river_discharge_in_the_last_24_hours",
)

ds = dataset.to_xarray()

```
