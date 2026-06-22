from bnti_core.scoring import calculate_final_index, category_weights, status_from_index


def test_weights_match_bnti():
    weights = category_weights()
    assert weights["military_conflict"] == 8.0
    assert weights["trade_agreement"] == -2.0


def test_index_formula():
    assert calculate_final_index(0) == 1.0
    assert 4.0 < calculate_final_index(2.5) < 5.5
    assert status_from_index(8.5) == "CRITICAL"
    assert status_from_index(3.0) == "STABLE"