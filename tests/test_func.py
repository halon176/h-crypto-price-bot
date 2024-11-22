from src.utility import max_column_size


def test_max_column_size():
    assert max_column_size(["a", "bb", "cczc"]) == 4
    assert max_column_size(["a", "bb", "cczc", ""]) == 4
    assert max_column_size(["a", "b" * 997, "c" * 998, "d" * 999]) == 999

    assert max_column_size([]) == 0
    assert max_column_size([""]) == 0
    assert max_column_size(["", ""]) == 0
    try:
        max_column_size([])
    except ValueError:
        assert True
