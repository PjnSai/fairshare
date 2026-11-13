import pytest

from splits.splitting import assign_leftover, split_with_leftover


def test_leftover_is_kept_separate():
    shares, leftover = split_with_leftover(1000, [1, 1, 1])
    assert shares == [333, 333, 333]
    assert leftover == 1


def test_no_leftover_when_it_divides_evenly():
    assert split_with_leftover(900, [1, 1, 1]) == ([300, 300, 300], 0)


def test_weighted_leftover():
    assert split_with_leftover(10, [1, 1, 2]) == ([2, 2, 5], 1)


def test_leftover_is_always_less_than_the_number_of_people():
    for total in range(0, 200):
        for people in range(1, 12):
            shares, leftover = split_with_leftover(total, [1] * people)
            assert 0 <= leftover < people
            assert sum(shares) + leftover == total


def test_assign_leftover_to_one_person():
    assert assign_leftover([333, 333, 333], 1, 2) == [333, 333, 334]


def test_assign_leftover_does_not_change_the_original_list():
    shares = [333, 333, 333]
    assign_leftover(shares, 1, 0)
    assert shares == [333, 333, 333]


def test_assigning_to_anyone_keeps_the_total_exact():
    shares, leftover = split_with_leftover(1000, [1, 1, 1])
    for person in range(3):
        assert sum(assign_leftover(shares, leftover, person)) == 1000


@pytest.mark.parametrize("person", [-1, 3, 10])
def test_assign_rejects_unknown_person(person):
    with pytest.raises(ValueError):
        assign_leftover([1, 2, 3], 1, person)


def test_assign_rejects_negative_leftover():
    with pytest.raises(ValueError):
        assign_leftover([1, 2, 3], -1, 0)
