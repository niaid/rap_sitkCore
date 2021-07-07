from my_pkg._util import helper


def test_util_helper():
    assert helper(0) == 0
    assert helper(1) == 1
    assert helper(2) == 1
    assert helper(3) == 2
    assert helper(4) == 3
    assert helper(6) == 8
    assert helper(9) == 34
    assert helper(15) == 610
