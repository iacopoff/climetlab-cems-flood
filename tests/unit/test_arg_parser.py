import pytest
from climetlab_cems_flood.utils import Parser
from climetlab_cems_flood import CONFIG



def assert_filter_time(years,months,days,expected):
    assert years == expected[0]
    assert months == expected[1]
    assert days == expected[2]

def test_parser_leadtime_hour():

    parser = Parser()
    step = 24
    assert parser.leadtime_hour("24-72/480-600", step) == [
        "24",
        "48",
        "72",
        "480",
        "504",
        "528",
        "552",
        "576",
        "600",
    ]

    assert parser.leadtime_hour("24-600", step) == [
        "24",
        "48",
        "72",
        "96",
        "120",
        "144",
        "168",
        "192",
        "216",
        "240",
        "264",
        "288",
        "312",
        "336",
        "360",
        "384",
        "408",
        "432",
        "456",
        "480",
        "504",
        "528",
        "552",
        "576",
        "600",
    ]

    assert parser.leadtime_hour("24-72/240-336/480-600", step) == [
        "24",
        "48",
        "72",
        "240",
        "264",
        "288",
        "312",
        "336",
        "480",
        "504",
        "528",
        "552",
        "576",
        "600",
    ]

@pytest.mark.parametrize("string, expected",[
                                                (
                                                    "2018/2020 01-12 01-31", #"20180101-20181231/20200101-20201231"
                                                    [
                                                    ["2018", "2020"],
                                                    ["%02d"%m for m in range(1,13)],
                                                    ["%02d"%d for d in range(1,32)]
                                                    ]
                                                ),
                                                                                                (
                                                    "2018/2020 01/02 01-25", #"20180201-20180212/20200101-20200125",
                                                    [
                                                    ["2018", "2020"],
                                                    ["01", "02"],
                                                    ["%02d"%d for d in range(1,26)]
                                                    ]
                                                ),
                                                #  (
                                                #     "2018/2020 01-02 01-12",#"20180212/20200101",
                                                #     [
                                                #     ["2018", "2020"],
                                                #     ["01","02"],
                                                #     ["01","12"]
                                                #     ]
                                                # ),
                                                 (
                                                    "2018 02 01",#"20180201",
                                                    [
                                                    ["2018"],
                                                    ["02"],
                                                    ["01"]
                                                    ]
                                                ),
                                                (
                                                    "2010-2021 01-12 01-31",#"20100101-20200325",
                                                    [
                                                    ["%d"%y for y in range(2010,2022,1)],
                                                    ["%02d"%m for m in range(1,13)],
                                                    ["%02d"%d for d in range(1,32)]
                                                    ]
                                                ),                                           
                                                pytest.param("202001-12/*1010", 42, marks=pytest.mark.xfail)
                                            ]
                        ) # expected = [[years],[months],[days]]
def test_parser_period(string,expected):
    
    parser = Parser()
    
    years, months, days = parser.time_filter(string, **CONFIG['glofas-historical']) 

    assert_filter_time(years,months,days,expected)

@pytest.mark.parametrize("string, expected",[
                                                (
                                                    "* 01 01",#"*0101",
                                                    [
                                                    ["%d"%y for y in range(1979,2023,1)],
                                                    ["01"],
                                                    ["01"]
                                                    ]
                                                ),
                                                                                                (
                                                    "* * *",
                                                    [
                                                    ["%d"%y for y in range(1979,2023,1)],
                                                    ["%02d"%m for m in range(1,13)],
                                                    ["%02d"%d for d in range(1,32)]
                                                    ]
                                                ),
                                                                                                (
                                                    "2020 * 01",#"2020*01",
                                                    [
                                                    ["2020"],
                                                    ["%02d"%m for m in range(1,13)],
                                                    ["01"]
                                                    ]
                                                ),
                                                (
                                                    "* 10-12 *",#"*10-12*",
                                                    [
                                                      ["%d"%y for y in range(1979,2023,1)],
                                                      ["10","11","12"],
                                                      ["%02d"%d for d in range(1,32)]  
                                                    ]

                                                ),
                                                (
                                                    "2000-2010 * *",#"2000-2010**",
                                                    [
                                                      ["%d"%y for y in range(2000,2011,1)],
                                                      ["%02d"%m for m in range(1,13)],
                                                      ["%02d"%d for d in range(1,32)]  
                                                    ]

                                                ) ,
                                                (
                                                    "* * 01-08",#"**01-08",
                                                    [
                                                      ["%d"%y for y in range(1979,2023,1)],
                                                      ["%02d"%m for m in range(1,13)],
                                                      ["01","02","03","04","05","06","07","08"]  
                                                    ]

                                                ) ,
                                                (
                                                    "2001-2005 01-05 *",#"2001-200501-05*",
                                                    [
                                                      ["%d"%y for y in range(2001,2006,1)],
                                                      ["%02d"%m for m in range(1,6)],
                                                      ["%02d"%d for d in range(1,32)] 
                                                    ]

                                                ) ,
                                                                                                (
                                                    "* 01-05 01-05",#"*01-0501-05",
                                                    [
                                                      ["%d"%y for y in range(1979,2023,1)],
                                                      ["%02d"%m for m in range(1,6)],
                                                      ["%02d"%d for d in range(1,6)] 
                                                    ]

                                                )  
                                            ]
                                                
                        )
def test_parser_period_star_param(string,expected):

    parser = Parser()

    years, months, days = parser.time_filter(string, **CONFIG['glofas-historical']) 


    assert_filter_time(years,months,days,expected)