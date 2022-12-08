% climetlab cems flood documentation master file, created by
% sphinx-quickstart on Fri May 20 12:27:00 2022.
% You can adapt this file completely to your liking, but it should at least
% contain the root `toctree` directive.

# Welcome to climetlab cems flood's documentation!

The `climetlab cems flood` package is a plugin of the [CliMetLab](https://climetlab.readthedocs.io/en/latest/index.html) Python package, to retrieve [Global Flood Awareness System (GloFAS)](https://www.globalfloods.eu/general-information/about-glofas/) data from the [Climate Data Store (CDS)](https://cds.climate.copernicus.eu/#!/home) distributed storage system.

It enables: 
- Filtering by time
- Filtering by (one or more) bounding box
- Extracting (one or more) point timeseries
- Caching functionality
- Parallel requests


```{note} EFAS is currently not available, the plan it to add it once it is produced on a latlon grid.
```

```{toctree}
:caption: 'Contents:'
:maxdepth: 2

installation.md
introduction.md
parameters.md
examples.md

```

