
Explain that the class' init parameters are post-processed to form the parameters to a cdsapi request.

# Dataset Parameters


## period

The period indicates the time intervals requested. The time intervals could be continuous from a date to another date or a set of fragmented time intervals.

The syntax follows these rules:

request one date

`20010505`

request many dates

`20010505/20020505/20030505`

request a period from a date to a date

`20010101-20011130`

request multiple separated periods

`20180201-20180212/20200101-20200315`

request all first of january

`*0101`

request everything

`***`

request all the first of the months of a year

`2000*01`

request a period of days for all years and months



request all months between a starting and ending year



request all the days for the years from 2001 to 2005 and months from January to May

`2001-200501-05*`

request the first 5 months and the first 5 days of all years:

`*01-0501-05`





There are three symbols that can instruct the interval request:
The hyphen `-` to indicate that you are requesting a start end

the star `*` to indicate everything and the slash `/` to indicate and.
a date is in the format %Y%m%d



You can easily check whether the string is actually returning what you are expecting


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




## split on