
"""Regression test for FM-08: reply amount differs from ledger."""

from types import SimpleNamespace

import pytest

from lab9.graders import ReplyLedgerCorrect
from lab9.trace_case import investigate


@pytest.mark.student
def test_lab9_fm08_reply_ledger_regression():
    broken = investigate("seeded_regression", "C-008", 11)
    fixed = investigate("fixed", "C-008", 11)

    grader = ReplyLedgerCorrect()

    broken_context = SimpleNamespace(
        output=broken["trial"],
        expected_output=broken["label"],
    )

    fixed_context = SimpleNamespace(
        output=fixed["trial"],
        expected_output=fixed["label"],
    )

    broken_result = grader.evaluate(broken_context)
    fixed_result = grader.evaluate(fixed_context)

    # The actual refund is correct in both variants.
    assert broken["trial"]["snapshot"]["refund_vnd"] == 20000
    assert fixed["trial"]["snapshot"]["refund_vnd"] == 20000

    # The buggy variant reports the wrong amount to the customer.
    assert broken_result.value is False

    # The corrected variant reports the ledger amount.
    assert fixed_result.value is True
