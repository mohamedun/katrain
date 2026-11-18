import pytest

from katrain.core.utils import ownership_sum_in_region

# KataGo stores the top row first; A1 is the first point of the bottom row.
OWNERSHIP = [0.91, -0.21, 0.13, -0.41, 0.51, -0.07]


@pytest.mark.parametrize(
    "region, expected",
    [
        ([0, 0, 0, 0], -0.41),  # A1, including a single point
        ([0, 1, 0, 0], 0.10),  # A1:B1, not the top row
        ([2, 2, 0, 1], 0.06),  # C1:C2
        ([2, 1, 1, 0], 0.36),  # Dragging from either direction is inclusive
        ([0, 2, 0, 1], 0.86),  # A full, non-square board is a valid selection
    ],
)
def test_sum_uses_board_coordinates(region, expected):
    assert ownership_sum_in_region(OWNERSHIP, (3, 2), region) == pytest.approx(expected)


def test_sum_keeps_precision_until_after_adding():
    total = ownership_sum_in_region([0.004, 0.004], (2, 1), [0, 1, 0, 0])
    assert total == pytest.approx(0.008)
    assert round(total, 2) == 0.01


@pytest.mark.parametrize("ownership", [None, [], [0.1], [float("nan")] * 6, [float("inf")] * 6])
def test_missing_or_nonfinite_analysis_has_no_sum(ownership):
    assert ownership_sum_in_region(ownership, (3, 2), [0, 2, 0, 1]) is None


@pytest.mark.parametrize("region", [[], [0, 0], [-1, 0, 0, 0], [0, 3, 0, 0], [0, 0, 0, 2]])
def test_outdated_or_invalid_selection_has_no_sum(region):
    assert ownership_sum_in_region(OWNERSHIP, (3, 2), region) is None
