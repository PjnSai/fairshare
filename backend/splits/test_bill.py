from fractions import Fraction

import pytest

from splits.splitting import (
    AmountsDoNotMatchTotal,
    Person,
    assign_leftover,
    split_bill,
    split_bill_with_leftover,
    split_by_weights,
    split_equally,
    split_exact,
)


def test_everyone_with_defaults_splits_equally():
    assert split_bill(1000, [Person(), Person(), Person()]) == split_equally(1000, 3)


def test_weights_only_behaves_like_split_by_weights():
    people = [Person(weight=1), Person(weight=1), Person(weight=2)]
    assert split_bill(10, people) == split_by_weights(10, [1, 1, 2])


def test_fixed_amounts_only_behaves_like_split_exact():
    people = [Person(1200, weight=0), Person(800, weight=0)]
    assert split_bill(2000, people) == split_exact(2000, [1200, 800])


def test_one_fixed_amount_and_the_rest_shared_equally():
    people = [Person(1200, weight=0), Person(), Person()]
    assert split_bill(2000, people) == [1200, 400, 400]


def test_everyone_has_their_own_items_and_shares_the_extras():
    # Own items 10.00, 15.00 and 5.00, plus 3.00 of shared costs split equally.
    people = [Person(1000), Person(1500), Person(500)]
    assert split_bill(3300, people) == [1100, 1600, 600]


def test_shared_costs_can_be_weighted():
    # The 4.00 of shared costs is split 2:1:1 instead of equally.
    people = [Person(1000, weight=2), Person(1500, weight=1), Person(500, weight=1)]
    assert split_bill(3400, people) == [1200, 1600, 600]


def test_someone_can_opt_out_of_the_shared_costs():
    people = [Person(1000), Person(1500), Person(500, weight=0)]
    assert split_bill(3300, people) == [1150, 1650, 500]


def test_leftover_pennies_in_the_shared_part_are_handled_automatically():
    people = [Person(100, weight=0), Person(), Person(), Person()]
    assert split_bill(1100, people) == [100, 334, 333, 333]


def test_fixed_amounts_that_use_up_the_bill_leave_nothing_to_share():
    people = [Person(2000, weight=0), Person(), Person()]
    assert split_bill(2000, people) == [2000, 0, 0]


def test_fixed_amounts_larger_than_the_bill_are_refused():
    people = [Person(800, weight=0), Person(500, weight=0), Person()]
    with pytest.raises(AmountsDoNotMatchTotal) as error:
        split_bill(1000, people)
    assert error.value.difference == 300


def test_a_remainder_nobody_has_agreed_to_pay_is_refused():
    people = [Person(1200, weight=0), Person(700, weight=0)]
    with pytest.raises(AmountsDoNotMatchTotal) as error:
        split_bill(2000, people)
    assert error.value.difference == -100


def test_with_leftover_keeps_the_leftover_separate():
    people = [Person(100, weight=0), Person(), Person(), Person()]
    amounts, leftover = split_bill_with_leftover(1100, people)
    assert amounts == [100, 333, 333, 333]
    assert leftover == 1


def test_creator_can_take_the_leftover_themselves():
    people = [Person(100, weight=0), Person(), Person(), Person()]
    amounts, leftover = split_bill_with_leftover(1100, people)
    assert assign_leftover(amounts, leftover, 0) == [101, 333, 333, 333]


def test_amounts_always_add_up_to_the_total():
    for total in range(0, 300, 7):
        for fixed in range(0, total + 1, 11):
            people = [Person(fixed), Person(weight=Fraction(1, 3)), Person(weight=2)]
            assert sum(split_bill(total, people)) == total


def test_with_leftover_amounts_plus_leftover_add_up_to_the_total():
    for total in range(0, 300, 7):
        for fixed in range(0, total + 1, 11):
            people = [Person(fixed), Person(weight=Fraction(1, 3)), Person(weight=2)]
            amounts, leftover = split_bill_with_leftover(total, people)
            assert sum(amounts) + leftover == total


@pytest.mark.parametrize(
    ("total", "people"),
    [
        (100, []),
        (-1, [Person()]),
        (100, [Person(-5), Person()]),
        (100, [Person(10.5), Person()]),
        (100, [Person(weight=-1), Person()]),
        (100, [Person(weight=0), Person(weight=0)]),
        (100, ["Sam", Person()]),
    ],
)
def test_rejects_bad_input(total, people):
    with pytest.raises(ValueError):
        split_bill(total, people)
