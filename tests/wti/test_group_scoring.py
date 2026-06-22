from bnti_core.groups import compute_group_index, compute_global_index


def test_g7_equal_weight():
    group = {"id": "g7", "name": "G7", "weighting": "gdp", "members": ["US", "GB", "DE"]}
    countries = {
        "US": {"index": 4.0},
        "GB": {"index": 2.0},
        "DE": {"index": 3.0},
    }
    registry = {
        "US": {"population": 100, "gdp_nominal_usd": 0},
        "GB": {"population": 100, "gdp_nominal_usd": 0},
        "DE": {"population": 100, "gdp_nominal_usd": 0},
    }
    result = compute_group_index(group, countries, registry)
    assert result["index"] == 3.0
    assert result["status"] == "STABLE"


def test_global_population_weight():
    registry = [
        {"iso2": "US", "population": 300},
        {"iso2": "IS", "population": 1},
    ]
    countries = {"US": {"index": 4.0}, "IS": {"index": 1.0}}
    idx = compute_global_index(countries, registry)
    assert 3.9 < idx < 4.0