from math import isclose

import pytest

from tests import Materials


def test_materials():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)

    assert mats["a"] == 1
    assert mats["b"] == 2
    assert mats["c"] == 3
    assert mats["d"] == 4
    assert mats["e"] == 5
    assert mats["f"] == 6


def test_materials_mul():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    mats = mats * 2

    assert mats["a"] == 2
    assert mats["b"] == 4
    assert mats["c"] == 6
    assert mats["d"] == 8
    assert mats["e"] == 10
    assert mats["f"] == 12


def test_materials_floordiv():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    mats = mats // 2

    assert mats["a"] == 0
    assert mats["b"] == 1
    assert mats["c"] == 1
    assert mats["d"] == 2
    assert mats["e"] == 2
    assert mats["f"] == 3


def test_materials_floordiv_by_material():
    numerator = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    denominator = Materials(e=2, f=1)

    assert numerator // denominator == 2


def test_materials_floordiv_by_zero():
    numerator = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    denominator = Materials()
    
    with pytest.raises(ZeroDivisionError):
        numerator / denominator


def test_materials_truediv():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    mats = mats / 2

    assert isclose(mats["a"], 0.5)
    assert isclose(mats["b"], 1.0)
    assert isclose(mats["c"], 1.5)
    assert isclose(mats["d"], 2.0)
    assert isclose(mats["e"], 2.5)
    assert isclose(mats["f"], 3.0)


def test_materials_truediv_by_material():
    numerator = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    denominator = Materials(e=2, f=1)

    assert numerator / denominator == 2.5


    numerator = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
def test_materials_truediv_by_zero():
    numerator = Materials(a=1, b=2, c=3, d=4, e=5, f=6)
    denominator = Materials()

    with pytest.raises(ZeroDivisionError):
        numerator / denominator


def test_materials_and():
    first = Materials(a=1, b=2, c=3, d=7)
    second = Materials(c=7, d=4, e=5, f=6)

    mats = first & second

    assert mats["a"] == 0
    assert mats["b"] == 0
    assert mats["c"] == 7
    assert mats["d"] == 7
    assert mats["e"] == 0
    assert mats["f"] == 0


def test_materials_or():
    first = Materials(a=1, b=2, c=3, d=7)
    second = Materials(c=7, d=4, e=5, f=6)

    mats = first | second

    assert mats["a"] == 1
    assert mats["b"] == 2
    assert mats["c"] == 7
    assert mats["d"] == 7
    assert mats["e"] == 5
    assert mats["f"] == 6


def test_materials_thresholding():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)

    less = mats < 3
    less_equal = mats <= 3
    greater = mats > 3
    greater_equal = mats >= 3


    assert less["a"] == 1
    assert less["b"] == 2
    assert less["c"] == 0
    assert less["d"] == 0
    assert less["e"] == 0
    assert less["f"] == 0

    assert less_equal["a"] == 1
    assert less_equal["b"] == 2
    assert less_equal["c"] == 3
    assert less_equal["d"] == 0
    assert less_equal["e"] == 0
    assert less_equal["f"] == 0

    assert greater["a"] == 0
    assert greater["b"] == 0
    assert greater["c"] == 0
    assert greater["d"] == 4
    assert greater["e"] == 5
    assert greater["f"] == 6

    assert greater_equal["a"] == 0
    assert greater_equal["b"] == 0
    assert greater_equal["c"] == 3
    assert greater_equal["d"] == 4
    assert greater_equal["e"] == 5
    assert greater_equal["f"] == 6

def test_materials_in():
    mats = Materials(a=1, b=2, c=3, d=4, e=5, f=6)

    assert "a" in mats
    assert "b" in mats
    assert "c" in mats
    assert "d" in mats
    assert "e" in mats
    assert "f" in mats
    assert "g" not in mats
    assert "h" not in mats
