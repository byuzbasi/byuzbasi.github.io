"""Bölüm 15 laboratuvarı: Welch, eşleştirilmiş ve ikili sonuç karşılaştırmaları."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def welch_summary(first: np.ndarray, second: np.ndarray) -> dict[str, float]:
    difference = float(first.mean() - second.mean())
    first_term = first.var(ddof=1) / first.size
    second_term = second.var(ddof=1) / second.size
    standard_error = float(np.sqrt(first_term + second_term))
    degrees_freedom = float(
        (first_term + second_term) ** 2
        / (first_term**2 / (first.size - 1) + second_term**2 / (second.size - 1))
    )
    t_observed = difference / standard_error
    p_value = float(2 * stats.t.sf(abs(t_observed), degrees_freedom))
    return {
        "fark": difference,
        "standart_hata": standard_error,
        "serbestlik_derecesi": degrees_freedom,
        "t": t_observed,
        "p": p_value,
    }


def main() -> None:
    coating_a = np.array([.27, .30, .34, .29, .36, .31, .25, .33, .28, .38, .32, .29])
    coating_b = np.array([.29, .41, .35, .46, .31, .38, .27, .43, .36, .34])
    welch = welch_summary(coating_a, coating_b)

    paired_differences = np.array([-1.2, -0.5, -0.9, -1.5, -0.4, -0.8, -1.1, -0.7])
    paired_test = stats.ttest_1samp(paired_differences, popmean=0)
    paired_interval = stats.t.interval(
        0.95,
        df=paired_differences.size - 1,
        loc=paired_differences.mean(),
        scale=stats.sem(paired_differences),
    )

    first_risk, second_risk = 0.08, 0.15
    risk_difference = first_risk - second_risk
    risk_ratio = first_risk / second_risk
    odds_ratio = (first_risk / (1 - first_risk)) / (second_risk / (1 - second_risk))

    assert np.isclose(paired_differences.mean(), -0.8875)
    assert np.isclose(paired_test.statistic, -6.818462884)
    assert np.allclose(paired_interval, [-1.195282569, -0.579717431])

    table = pd.DataFrame([welch])
    print("Welch özeti")
    print(table.round(5).to_string(index=False))
    print("\nEşleştirilmiş fark aralığı:", np.round(paired_interval, 4))
    print(
        "İkili etkiler:",
        {"risk farkı": round(risk_difference, 4), "risk oranı": round(risk_ratio, 4), "olasılık oranı": round(odds_ratio, 4)},
    )


if __name__ == "__main__":
    main()
