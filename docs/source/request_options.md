# Request options

# Filtering

Filtering can dramaticaly reduce the volume of data to download, focusing only over period or location of interest.

## Temporal

The `temporal_filter` keyword allows requesting specific period or interval of time. </br>
The `temporal_filter` syntax is simple: for selecting multiple non consecutive or consecutive years, months, days, use these operators:

- `-` (FROM-TO) 
- `/` (AND)
- `*` (ALL)

to compose a date that follows the format `%Y %m %d`. </br>
For example:

| description        |  year (%Y) | month (%m)|  day  (%d)| temporal filter |
|--------|:-----:|:-----:|:-----:|-------------|
| Request one single date       |   2000  |   01  |   01  | "2000 01 01"     |             |
| Request JJA between 2020 and 2022| 2020-2022 | 06-08 | * | "2020-2022 06-08 *"|             |
| Request the first 2 weeks of every Jan and Feb of three non consecutive years| 2000/2003/2015 | 01-02 | 01-15 | "2000/2003/2015 01-02 01-15"|             |
| Request every 15th of June accross all the years |   *   |   06   |   *   | "* 06 15"       |             |


In case you are in doubt, before sending a request you can easily check whether the `temporal_filter` is returning what you intended:


```python
>>> from climetlab_cems_flood.utils import show_request_for_parameter
>>> show_request_for_parameter('cems-glofas-historical', 'temporal_filter', '2012/2021 01-10 12-18')

years: ['2012', '2021']
months: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
days: ['12', '13', '14', '15', '16', '17', '18']


>>> show_request_for_parameter('cems-glofas-seasonal', 'temporal_filter', '* 07 *')

years: ['2019', '2020', '2021', '2022']
months: ['07']
days: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
```

## Spatial

### by bounding box (area)

You can define a bounding box:

`north, west, south, east`

You can also pass a list of areas..

### by points (coords)


## Parallel requests

 The `split_on` parameter allows splitting the request into multiple requests to the CDS.

For example, this is how you would send a request per year and per month:

```python
hist = cml.load_dataset(
            'cems-flood-glofas-historical',
            model='lisflood',
            product_type='intermediate',
            system_version='version_3_1',
            period= '20000101-20201231',
            variable="river_discharge_in_the_last_24_hours",
            split_on = ['hyear','hmonth'],
            threads = 6,
        )

```

The `threads` parameters indicate the number of concurrent requests are sent to the CDS. 

Please check the CDS website for how many concurrent request you are allowed to send.


It is also possible to split by area in case you are requesting a list of areas
