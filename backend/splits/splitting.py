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
