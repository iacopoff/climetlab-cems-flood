import pytest
from climetlab_cems_flood.utils import build_multi_request, preprocess_spatial_filter


def req_multy_area():
    REQUEST =  {
                "system_version": "operational",
                "hydrological_model": "lislfood",
                "product_type": "control_forecast",
                "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
                "year": ['2000', '2001'],
                "month": ['01','02'],
                "day": '01',
                "leadtime_hour": ['24', '48', '72', '96', '120'],
                "area": [
                        {'name': 'area1', 'area': [10, 5, 10, 5]},
                        {'name': 'area2', 'area': [20, 40, 20, 40]},
                        {'name': 'area3', 'area': [-1, -1, -1, -1]}
                        ],
                "format": "grib",
            }
    return REQUEST


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'], ['area-area1', 'area-area2', 'area-area3']),
                            (['area', ('leadtime_hour', 2)], ['area-area1_lh-120',
                                                              'area-area1_lh-24-48',
                                                              'area-area1_lh-72-96',
                                                              'area-area2_lh-120',
                                                              'area-area2_lh-24-48', 
                                                              'area-area2_lh-72-96',
                                                              'area-area3_lh-120', 
                                                              'area-area3_lh-24-48',
                                                              'area-area3_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area-area1_year-2000_variable-rivo',
                                                                 'area-area1_year-2000_variable-swe',
                                                                 'area-area1_year-2001_variable-rivo',
                                                                 'area-area1_year-2001_variable-swe',
                                                                 'area-area2_year-2000_variable-rivo',
                                                                 'area-area2_year-2000_variable-swe',
                                                                 'area-area2_year-2001_variable-rivo',
                                                                 'area-area2_year-2001_variable-swe',
                                                                 'area-area3_year-2000_variable-rivo',
                                                                 'area-area3_year-2000_variable-swe', 
                                                                 'area-area3_year-2001_variable-rivo', 
                                                                 'area-area3_year-2001_variable-swe'])
                        ])
def test_multy_area(split_on, expected):
    req = req_multy_area()
    sf_ids = preprocess_spatial_filter(req, req['area'], None)
    _, output_names = build_multi_request(req, split_on, sf_ids, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected


def req_single_area():
    REQUEST_SINGLE_AREA =  {
                "system_version": "operational",
                "hydrological_model": "lislfood",
                "product_type": "control_forecast",
                "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
                "year": ['2000', '2001'],
                "month": ['01','02'],
                "day": '01',
                "leadtime_hour": ['24', '48', '72', '96', '120'],
                "area": [
                        {'name': 'area1', 'area': [10, 5, 10, 5]},
                        ],
                "format": "grib",
            }
    return REQUEST_SINGLE_AREA


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'], ['area-area1']),
                            (['area', ('leadtime_hour', 2)], ['area-area1_lh-120',
                                                              'area-area1_lh-24-48',
                                                              'area-area1_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area-area1_year-2000_variable-rivo',
                                                                 'area-area1_year-2000_variable-swe',
                                                                 'area-area1_year-2001_variable-rivo',
                                                                 'area-area1_year-2001_variable-swe'])
                        ])
def test_single_area(split_on, expected):
    req = req_single_area()
    sf_ids = preprocess_spatial_filter(req, req['area'], None)
    _, output_names = build_multi_request(req, split_on, sf_ids, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected




def req_multy_coords():
    REQUEST2 =  {
                "system_version": "operational",
                "hydrological_model": "lislfood",
                "product_type": "control_forecast",
                "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
                "year": ['2000', '2001'],
                "month": ['01','02'],
                "day": '01',
                "leadtime_hour": ['24','48','72','96','120'],
                "coords":[{'name': 'st1', 'lat': 10, 'lon': 5},
                        {'name': 'st2', 'lat': 20, 'lon': 40},
                        {'name': 'st3', 'lat': -1, 'lon': -1},
                        ],
                "format": "grib"
            }
    return REQUEST2


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'], ['area-st1', 'area-st2', 'area-st3']),
                            (['area', ('leadtime_hour', 2)], ['area-st1_lh-120',
                                                              'area-st1_lh-24-48',
                                                              'area-st1_lh-72-96',
                                                              'area-st2_lh-120',
                                                              'area-st2_lh-24-48', 
                                                              'area-st2_lh-72-96',
                                                              'area-st3_lh-120', 
                                                              'area-st3_lh-24-48',
                                                              'area-st3_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area-st1_year-2000_variable-rivo',
                                                                 'area-st1_year-2000_variable-swe',
                                                                 'area-st1_year-2001_variable-rivo',
                                                                 'area-st1_year-2001_variable-swe',
                                                                 'area-st2_year-2000_variable-rivo',
                                                                 'area-st2_year-2000_variable-swe',
                                                                 'area-st2_year-2001_variable-rivo',
                                                                 'area-st2_year-2001_variable-swe',
                                                                 'area-st3_year-2000_variable-rivo',
                                                                 'area-st3_year-2000_variable-swe', 
                                                                 'area-st3_year-2001_variable-rivo', 
                                                                 'area-st3_year-2001_variable-swe'])
                        ]
                        )
def test_multy_coords(split_on, expected):
    req = req_multy_coords()
    sf_ids = preprocess_spatial_filter(req, None, req['coords'])
    _, output_names = build_multi_request(req, split_on, sf_ids, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected
    
    
    
    

def req_single_coords():
    REQUEST_SINGLE_COORD =  {
                "system_version": "operational",
                "hydrological_model": "lislfood",
                "product_type": "control_forecast",
                "variable": ["river_discharge_in_the_last_24_hours","snow_melt_water_equivalent"],
                "year": ['2000', '2001'],
                "month": ['01', '02'],
                "day": '01',
                "leadtime_hour": ['24', '48', '72', '96', '120'],
                "coords": [{'name': 'st1', 'lat': 10, 'lon': 5}],
                "format": "grib"
            }
    return REQUEST_SINGLE_COORD


@pytest.mark.parametrize('split_on,expected',
                        [   
                            (['area'], ['area-st1']),
                            (['area', ('leadtime_hour', 2)], ['area-st1_lh-120',
                                                              'area-st1_lh-24-48',
                                                              'area-st1_lh-72-96']),
                            (['area', 'year', ('variable', 1)], ['area-st1_year-2000_variable-rivo',
                                                                 'area-st1_year-2000_variable-swe',
                                                                 'area-st1_year-2001_variable-rivo',
                                                                 'area-st1_year-2001_variable-swe'])
                        ]
                        )
def test_single_coords(split_on, expected):
    req = req_single_coords()
    sf_ids = preprocess_spatial_filter(req, None, req['coords'])
    _, output_names = build_multi_request(req, split_on, sf_ids, dataset='cems-glofas-forecast')

    expected.sort()
    output_names.sort()

    assert output_names == expected