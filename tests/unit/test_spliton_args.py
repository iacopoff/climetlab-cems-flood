import pytest
from climetlab_cems_flood.utils import build_multi_request, preprocess_spatial_filter



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
                            (['area'], ['area-10-5-10-5', 'area-20-40-20-40', 'area--1--1--1--1']),
                            (['area', ('leadtime_hour', 2)], ['area--1--1--1--1_lh-120',
                                                              'area--1--1--1--1_lh-24-48',
                                                              'area--1--1--1--1_lh-72-96',
                                                              'area-10-5-10-5_lh-120',
                                                              'area-10-5-10-5_lh-24-48', 
                                                              'area-10-5-10-5_lh-72-96',
                                                              'area-20-40-20-40_lh-120', 
                                                              'area-20-40-20-40_lh-24-48',
                                                              'area-20-40-20-40_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area--1--1--1--1_year-2000_variable-rivo',
                                                                 'area--1--1--1--1_year-2000_variable-swe',
                                                                 'area--1--1--1--1_year-2001_variable-rivo',
                                                                 'area--1--1--1--1_year-2001_variable-swe',
                                                                 'area-10-5-10-5_year-2000_variable-rivo',
                                                                 'area-10-5-10-5_year-2000_variable-swe',
                                                                 'area-10-5-10-5_year-2001_variable-rivo',
                                                                 'area-10-5-10-5_year-2001_variable-swe',
                                                                 'area-20-40-20-40_year-2000_variable-rivo',
                                                                 'area-20-40-20-40_year-2000_variable-swe', 
                                                                 'area-20-40-20-40_year-2001_variable-rivo', 
                                                                 'area-20-40-20-40_year-2001_variable-swe'])
                        ]
                        
                        )
def test1(split_on, expected):
    preprocess_spatial_filter(REQUEST, REQUEST['area'], None)
    _, output_names = build_multi_request(REQUEST, split_on, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected


REQUEST2 =  {
            "system_version": "operational",
            "hydrological_model": "lislfood",
            "product_type": "control_forecast",
            "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
            "year": ['2000', '2001'],
            "month": ['01','02'],
            "day": '01',
            "leadtime_hour": ['24','48','72','96','120'],
            "coords":[[10,5],[20,40],[-1,-1]],
            "format": "grib"
        }


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'], ['area-10-5-10-5', 'area-20-40-20-40', 'area--1--1--1--1']),
                            (['area', ('leadtime_hour', 2)], ['area--1--1--1--1_lh-120',
                                                              'area--1--1--1--1_lh-24-48',
                                                              'area--1--1--1--1_lh-72-96',
                                                              'area-10-5-10-5_lh-120',
                                                              'area-10-5-10-5_lh-24-48', 
                                                              'area-10-5-10-5_lh-72-96',
                                                              'area-20-40-20-40_lh-120', 
                                                              'area-20-40-20-40_lh-24-48',
                                                              'area-20-40-20-40_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area--1--1--1--1_year-2000_variable-rivo',
                                                                 'area--1--1--1--1_year-2000_variable-swe',
                                                                 'area--1--1--1--1_year-2001_variable-rivo',
                                                                 'area--1--1--1--1_year-2001_variable-swe',
                                                                 'area-10-5-10-5_year-2000_variable-rivo',
                                                                 'area-10-5-10-5_year-2000_variable-swe',
                                                                 'area-10-5-10-5_year-2001_variable-rivo',
                                                                 'area-10-5-10-5_year-2001_variable-swe',
                                                                 'area-20-40-20-40_year-2000_variable-rivo',
                                                                 'area-20-40-20-40_year-2000_variable-swe', 
                                                                 'area-20-40-20-40_year-2001_variable-rivo', 
                                                                 'area-20-40-20-40_year-2001_variable-swe'])
                        ]
                        )
def test2(split_on, expected):
    preprocess_spatial_filter(REQUEST2, None, REQUEST2['coords'])
    _, output_names = build_multi_request(REQUEST2, split_on, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected