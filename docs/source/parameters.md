


# Parameters


## period

The period indicates the time intervals requested. The time intervals could be continuous from a date to another date or a set of fragmented time intervals.


Examples that speak a thousand words:

- Request one date

`20010505`

- Request many dates

- `20010505/20020505/20030505`

- Request a time interval from a starting date to a end date

`20010101-20011130`

- Request two (but could be more) non consecutive time intervals

`20180201-20180212/20200101-20200315`

- Request every first of January

`*0101`

- Request everything

`***`

- Request the fifteenth of the month of each month in year 2000

`2000*15`

- Request every days bweteen 2001 and 2005 and between January and May

`2001-200501-05*`

- Request the first 5 months and the days between the 20th and 25th for all years available:

`*01-0520-25`


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

## area

You can define a bounding box:

`north, west, south, east`

You can also pass a list of areas..

## split_on and threads 

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

## merger