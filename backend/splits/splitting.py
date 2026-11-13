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
