# Request parameters

# Filtering

## Temporal

There are different options for selecting multiple non consecutive or consecutive years, months, days. 

|        |  year | month |  day  |  example      | explanation |
|--------|:-----:|:-----:|:-----:|---------------|-------------|
|**operator**|       |       |       |               |             |
|        |   %Y  |   %m  |   %d  |2000 01 01     |             |
|**-** (from-to) | %Y-%Y | %m-%m | %d-%d |2000 01-10 01  |             |
|**/** (and)     | %Y/%Y | %m/%m | %d/%d |2000/2003/2005 01 01|             |
|**\*** (all)     |   *   |   *   |   *   |* 01 01        |             |


In case you are in doubt, before sending a request you can easily check whether the string is actually returning what you were expecting:


```python
>>> from climetlab_cems_flood.utils import Parser
>>> string = "2001-200501-05*"
>>> years, months, days = Parser().period(string)
>>> print(years)
['2001', '2002', '2003', '2004', '2005']
>>> print(months)
['01', '02', '03', '04', '05']
>>> print(days)
['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
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
