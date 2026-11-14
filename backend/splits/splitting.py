from dataclasses import dataclass
from fractions import Fraction
from math import floor


def split_equally(total_pence: int, count: int) -> list[int]:
    """Split a total in pence between `count` people, never losing a penny.

    Any leftover pennies go one each to the first people in the list.
    """
    if total_pence < 0:
        raise ValueError("total_pence cannot be negative")
    if count < 1:
        raise ValueError("count must be at least 1")

    base, leftover = divmod(total_pence, count)
    return [base + 1 if i < leftover else base for i in range(count)]


def _floor_shares(
    total_pence: int, weights: list[Fraction | int]
) -> tuple[list[Fraction], list[int], int]:
    """Validate the input, then return the exact shares, the shares rounded
    down to whole pennies, and the number of pennies left over."""
    if total_pence < 0:
        raise ValueError("total_pence cannot be negative")
    if not weights:
        raise ValueError("at least one weight is required")

    exact_weights = [Fraction(weight) for weight in weights]
    if any(weight < 0 for weight in exact_weights):
        raise ValueError("weights cannot be negative")
    weight_total = sum(exact_weights)
    if weight_total == 0:
        raise ValueError("weights cannot all be zero")

    exact_shares = [total_pence * weight / weight_total for weight in exact_weights]
    parts = [floor(share) for share in exact_shares]
    return exact_shares, parts, total_pence - sum(parts)


def split_by_weights(total_pence: int, weights: list[Fraction | int]) -> list[int]:
    """Split a total in pence in proportion to weights, never losing a penny.

    Each person first gets the whole pennies they are owed. Any pennies left over
    go to the people with the largest discarded fractions (earlier person wins a tie).
    """
    exact_shares, parts, leftover = _floor_shares(total_pence, weights)

    by_largest_remainder = sorted(
        range(len(parts)), key=lambda i: (-(exact_shares[i] - parts[i]), i)
    )
    for i in by_largest_remainder[:leftover]:
        parts[i] += 1
    return parts


def split_with_leftover(
    total_pence: int, weights: list[Fraction | int]
) -> tuple[list[int], int]:
    """Split in proportion to weights, but do not hand out the leftover pennies.

    Returns each person's share rounded down, and the leftover as a separate number
    so that the bill's creator can decide who gets it.
    """
    _, parts, leftover = _floor_shares(total_pence, weights)
    return parts, leftover


def assign_leftover(shares: list[int], leftover: int, person_index: int) -> list[int]:
    """Return a copy of `shares` with the leftover pennies added to one person."""
    if leftover < 0:
        raise ValueError("leftover cannot be negative")
    if not 0 <= person_index < len(shares):
        raise ValueError("person_index is out of range")

    result = list(shares)
    result[person_index] += leftover
    return result


class AmountsDoNotMatchTotal(ValueError):
    """The exact amounts do not add up to the bill."""

    def __init__(self, total_pence: int, amounts_total: int) -> None:
        self.difference = amounts_total - total_pence
        if self.difference > 0:
            detail = f"{self.difference}p too much"
        else:
            detail = f"{-self.difference}p short"
        super().__init__(
            f"amounts add up to {amounts_total}p but the bill is "
            f"{total_pence}p ({detail})"
        )


def split_exact(total_pence: int, amounts: list[int]) -> list[int]:
    """Check that exact amounts add up to the bill, and return them.

    Nothing is rescaled: if the amounts do not match the total, say by how much.
    """
    if total_pence < 0:
        raise ValueError("total_pence cannot be negative")
    if not amounts:
        raise ValueError("at least one amount is required")
    if not all(isinstance(amount, int) for amount in amounts):
        raise ValueError("amounts must be whole pennies")
    if any(amount < 0 for amount in amounts):
        raise ValueError("amounts cannot be negative")

    amounts_total = sum(amounts)
    if amounts_total != total_pence:
        raise AmountsDoNotMatchTotal(total_pence, amounts_total)
    return list(amounts)


@dataclass(frozen=True)
class Person:
    """What one person owes: a fixed amount, plus a share of whatever is left.

    `fixed_pence` is what they owe regardless, such as their own items. `weight` is
    their share of the rest once every fixed amount is taken out: the default of 1
    is an equal share, and 0 means they do not share in it.
    """

    fixed_pence: int = 0
    weight: Fraction | int = 1


def _take_out_fixed(
    total_pence: int, people: list[Person]
) -> tuple[list[int], int, list[Fraction | int]]:
    """Validate the input, then return each person's fixed amount, the pennies left
    after all the fixed amounts, and each person's weight for sharing those pennies."""
    if total_pence < 0:
        raise ValueError("total_pence cannot be negative")
    if not people:
        raise ValueError("at least one person is required")
    if not all(isinstance(person, Person) for person in people):
        raise ValueError("each person must be a Person")

    fixed = [person.fixed_pence for person in people]
    if not all(isinstance(amount, int) and amount >= 0 for amount in fixed):
        raise ValueError("fixed amounts must be whole pennies and not negative")
    weights = [person.weight for person in people]
    if any(Fraction(weight) < 0 for weight in weights):
        raise ValueError("weights cannot be negative")

    fixed_total = sum(fixed)
    if fixed_total > total_pence:
        raise AmountsDoNotMatchTotal(total_pence, fixed_total)
    remainder = total_pence - fixed_total
    if remainder > 0 and all(Fraction(weight) == 0 for weight in weights):
        raise AmountsDoNotMatchTotal(total_pence, fixed_total)
    return fixed, remainder, weights


def split_bill(total_pence: int, people: list[Person]) -> list[int]:
    """Split a bill where each person owes a fixed amount plus a share of the rest.

    Leftover pennies in the shared part go to the largest remainders, as in
    split_by_weights. If the amounts cannot add up to the bill, it refuses.
    """
    fixed, remainder, weights = _take_out_fixed(total_pence, people)
    if remainder == 0:
        return fixed
    shares = split_by_weights(remainder, weights)
    return [f + s for f, s in zip(fixed, shares, strict=True)]


def split_bill_with_leftover(
    total_pence: int, people: list[Person]
) -> tuple[list[int], int]:
    """Like split_bill, but return the leftover pennies separately so the bill's
    creator can choose who gets them."""
    fixed, remainder, weights = _take_out_fixed(total_pence, people)
    if remainder == 0:
        return fixed, 0
    shares, leftover = split_with_leftover(remainder, weights)
    return [f + s for f, s in zip(fixed, shares, strict=True)], leftover
