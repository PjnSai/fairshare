from fractions import Fraction

import pytest

from splits.splitting import split_by_weights, split_equally


def test_equal_weights_match_split_equally():
    for total in range(0, 100):
        for people in range(1, 8):
            assert split_by_weights(total, [1] * people) == split_equally(total, people)


def test_half_and_two_quarters():
    weights = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)]
    assert split_by_weights(1000, weights) == [500, 250, 250]


def test_thirds_of_a_pound():
    assert split_by_weights(100, [Fraction(1, 3)] * 3) == [34, 33, 33]


def test_weights_do_not_need_to_add_up_to_one():
    assert split_by_weights(900, [2, 1]) == [600, 300]


def test_leftover_penny_goes_to_the_largest_remainder():
    assert split_by_weights(10, [1, 1, 2]) == [3, 2, 5]


def test_zero_weight_pays_nothing():
    assert split_by_weights(100, [1, 0, 1]) == [50, 0, 50]


def test_parts_always_add_up_to_the_total():
    weight_sets = [
        [1, 2, 3],
        [Fraction(1, 3), Fraction(1, 6), Fraction(1, 2)],
        [5, 5, 5, 5, 1],
    ]
    for total in range(0, 300, 7):
        for weights in weight_sets:
            assert sum(split_by_weights(total, weights)) == total


@pytest.mark.parametrize(
    ("total", "weights"),
    [
        (100, []),
        (100, [0, 0]),
        (100, [1, -1]),
        (-1, [1, 1]),
    ],
)
def test_rejects_bad_input(total, weights):
    with pytest.raises(ValueError):
        split_by_weights(total, weights)
