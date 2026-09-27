"""Small, transparent helpers used in the introductory chapters.

The functions keep formulas visible for teaching. Later chapters use SciPy and
statsmodels directly where a tested library implementation is preferable.
"""

from __future__ import annotations

from math import fsum, sqrt
from typing import Iterable


def mean(values: Iterable[float]) -> float:
    data = tuple(float(value) for value in values)
    if not data:
        raise ValueError("mean requires at least one observation")
    return fsum(data) / len(data)


def sample_variance(values: Iterable[float]) -> float:
    data = tuple(float(value) for value in values)
    if len(data) < 2:
        raise ValueError("sample variance requires at least two observations")
    center = mean(data)
    return fsum((value - center) ** 2 for value in data) / (len(data) - 1)


def sample_standard_deviation(values: Iterable[float]) -> float:
    return sqrt(sample_variance(values))


def posterior_defect(
    prevalence: float,
    sensitivity: float,
    specificity: float,
) -> float:
    for name, value in {
        "prevalence": prevalence,
        "sensitivity": sensitivity,
        "specificity": specificity,
    }.items():
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    true_alarm = sensitivity * prevalence
    false_alarm = (1 - specificity) * (1 - prevalence)
    denominator = true_alarm + false_alarm
    if denominator == 0:
        raise ValueError("alarm has zero probability")
    return true_alarm / denominator


def series_reliability(component_reliabilities: Iterable[float]) -> float:
    result = 1.0
    seen = False
    for reliability in component_reliabilities:
        if not 0 <= reliability <= 1:
            raise ValueError("reliability must be between 0 and 1")
        result *= reliability
        seen = True
    if not seen:
        raise ValueError("at least one component is required")
    return result


def parallel_reliability(component_reliabilities: Iterable[float]) -> float:
    joint_failure = 1.0
    seen = False
    for reliability in component_reliabilities:
        if not 0 <= reliability <= 1:
            raise ValueError("reliability must be between 0 and 1")
        joint_failure *= 1 - reliability
        seen = True
    if not seen:
        raise ValueError("at least one component is required")
    return 1 - joint_failure
