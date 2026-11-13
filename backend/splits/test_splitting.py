import pytest

from splits.splitting import split_equally


def test_even_split():
    assert split_equally(900, 3) == [300, 300, 300]


def test_leftover_pennies_go_to_the_first_people():
    assert split_equally(1000, 3) == [334, 333, 333]


def test_parts_always_add_up_to_the_total():
    for total in range(0, 200):
        for count in range(1, 12):
            assert sum(split_equally(total, count)) == total


def test_zero_total():
    assert split_equally(0, 4) == [0, 0, 0, 0]


def test_rejects_zero_people():
    with pytest.raises(ValueError):
        split_equally(100, 0)


def test_rejects_negative_total():
    with pytest.raises(ValueError):
        split_equally(-1, 2)
