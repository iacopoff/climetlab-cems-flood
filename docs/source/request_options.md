# Request options

A request is composed by three groups of keywords:
- The keywords to select the attributes of the product (`model`, `product type`, `system version`, etc.). 
- The keywords to spatially and temporally filter the product (`temporal_filter`, `area`, `coords`). 
- The keywords that specify how the request should be sent to the CDS ('split_on' and 'threads'). 

## Filtering

Filtering can dramaticaly reduce the volume of data to download.

### Temporal Filtering

The `temporal_filter` keyword allows requesting specific period or interval of time. </br>
The syntax is simple: for selecting multiple non consecutive or consecutive years, months, days, use these operators: `-` (FROM-TO), `/` (AND), `*` (ALL), to compose a date that follows the format `%Y %m %d`. </br>

For example:

| Description        |  Year (%Y) | Month (%m)|  Day  (%d)| temporal_filter string|
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

### Spatial Filtering

It is possible to request one or more **areas** or one or more **point coordinates**.

```{warning} 
When requesting multiple areas or point coordinates always declare the `split_on` parameter 
```

The `area` keyword accepts a **bounding box** with a sequence of coordinates following: `[north, west, south, east]`, such as:

```python
area = [{"name":"rhine", "area":[50.972204,5.450796, 46.296530, 11.871059]}]
```
In case you want to request multiple areas, then do like:

```python
area = [
    {"name":"rhine", "area":[50.972204,5.450796, 46.296530, 11.871059]},
    {"name":"po", "area":[46.62980, 6.55, 44.05381, 12.554784]}]
```

To request **point coordinates**, use the `coords` keyword:

```python
coords = [
    {'name':'pontelagoscuro','lat':44.886111, 'lon':11.604444},
    {'name':'casale-monferrato','lat':45.142222, 'lon':8.447500},
    {'name':'canonica-dadda', 'lat':45.576944, 'lon':9.534722}]
```

```{note} The CDS always returns 4 grid cells when requesting a point coordinate. 
Once the request is completed, use the `show_coords` method to inspect the location.
Look for usage of the `show_coords` method in the tutorial section.
 ```

## Speed up requests

The CDS limits the number of requests and the amount of data per product that is possible to retrieve in the scope of an individual request.

The `split_on` keyword allows sending parallel requests to the CDS, overcoming those limits. 
It is possible to split the request into sub-requests, specifying the keywords to split on, for example: `split_on=["area", "year", "month"]`. It is also possible to specify how many items to request per sub-request, using the format `split_on=[("year", 3), ("month",6)]`.

```{warning} 
For multiple spatial requests, it is mandatory to split on "area" or "coords"
```

Use the `threads` keyword to allocate the pool of threads to send parallel sub-requests (n. of threads ~ n. of sub-requests). 

```{note} Reforecast and historical products require an "h" before "year"-> "hyear", "month"->"hmonth", "day"->"hday" 
```

For example, the following request send sub-requests in "chunks" of 4-year and 6-months

```python
hist = cml.load_dataset(
            'glofas-historical',
            model='lisflood',
            product_type='intermediate',
            system_version='version_3_1',
            temporal_filter= '2000-2020 * *',
            variable="river_discharge_in_the_last_24_hours",
            split_on = [('hyear', 4), ('hmonth',6)],
            threads = 12
        )

```
