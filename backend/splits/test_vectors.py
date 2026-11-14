import json
from fractions import Fraction
from pathlib import Path

import pytest

from splits.splitting import (
    AmountsDoNotMatchTotal,
    Person,
    split_bill,
    split_bill_with_leftover,
    split_by_weights,
    split_equally,
    split_exact,
)

VECTORS_FILE = (
    Path(__file__).resolve().parents[2] / "shared" / "test-vectors" / "splits.json"
)
CASES = json.loads(VECTORS_FILE.read_text(encoding="utf-8"))["cases"]


def _people(raw_people):
    return [
        Person(fixed_pence=p.get("fixed", 0), weight=Fraction(p.get("weight", 1)))
        for p in raw_people
    ]


def _run(function, data):
    if function == "split_equally":
        return split_equally(data["total"], data["count"])
    if function == "split_by_weights":
        return split_by_weights(data["total"], [Fraction(w) for w in data["weights"]])
    if function == "split_exact":
        return split_exact(data["total"], data["amounts"])
    if function == "split_bill":
        return split_bill(data["total"], _people(data["people"]))
    if function == "split_bill_with_leftover":
        amounts, leftover = split_bill_with_leftover(
            data["total"], _people(data["people"])
        )
        return {"amounts": amounts, "leftover": leftover}
    raise AssertionError(f"unknown function in the test vectors: {function}")


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_vector(case):
    function, data = case["function"], case["input"]
    if "error" not in case:
        assert _run(function, data) == case["expected"]
    elif case["error"] == "mismatch":
        with pytest.raises(AmountsDoNotMatchTotal) as error:
            _run(function, data)
        assert error.value.difference == case["difference"]
    else:
        with pytest.raises(ValueError) as error:
            _run(function, data)
        assert not isinstance(error.value, AmountsDoNotMatchTotal)
