import pytest

from splits.splitting import AmountsDoNotMatchTotal, split_exact


def test_exact_amounts_that_add_up_are_returned():
    assert split_exact(2000, [1200, 800]) == [1200, 800]


def test_amounts_can_be_equal_or_uneven():
    assert split_exact(3000, [1000, 1000, 1000]) == [1000, 1000, 1000]


def test_a_zero_amount_is_allowed():
    assert split_exact(500, [500, 0]) == [500, 0]


def test_returns_a_copy():
    amounts = [1200, 800]
    result = split_exact(2000, amounts)
    result[0] = 0
    assert amounts == [1200, 800]


def test_too_little_reports_a_negative_difference():
    with pytest.raises(AmountsDoNotMatchTotal) as error:
        split_exact(2000, [1200, 700])
    assert error.value.difference == -100


def test_too_much_reports_a_positive_difference():
    with pytest.raises(AmountsDoNotMatchTotal) as error:
        split_exact(2000, [1200, 900])
    assert error.value.difference == 100


def test_message_says_how_far_off_the_amounts_are():
    with pytest.raises(AmountsDoNotMatchTotal, match="100p short"):
        split_exact(2000, [1200, 700])


def test_a_mismatch_is_also_a_value_error():
    with pytest.raises(ValueError):
        split_exact(2000, [1, 1])


@pytest.mark.parametrize(
    ("total", "amounts"),
    [
        (100, []),
        (100, [150, -50]),
        (-1, [0]),
    ],
)
def test_rejects_bad_input(total, amounts):
    with pytest.raises(ValueError):
        split_exact(total, amounts)


def test_rejects_fractions_of_a_penny():
    with pytest.raises(ValueError):
        split_exact(100, [50.5, 49.5])
