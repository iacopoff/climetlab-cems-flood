import pytest
from climetlab_cems_flood.utils import build_multi_request



REQUEST =  {
            "system_version": "operational",
            "hydrological_model": "lislfood",
            "product_type": "control_forecast",
            "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
            "year": ['2000', '2001'],
            "month": ['01','02'],
            "day": '01',
            "leadtime_hour": ['24','48','72','96','120'],
            "area": [[10,5,10,5],[20,40,20,40],[-1,-1,-1,-1]],
            "format": "grib",
        }


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'],['area-10-5-10-5','area-20-40-20-40','area--1--1--1--1']),
                            ([('leadtime_hour', 2)], ['lh-24-48', 'lh-72-96','lh-120'] ),
                            (['year',('variable', 1)], ['year-2000_variable-rivo','year-2000_variable-swe','year-2001_variable-swe','year-2001_variable-rivo'])
                        ]
                        
                        )
def test(split_on, expected):
    _, output_names = build_multi_request(REQUEST, split_on, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected
