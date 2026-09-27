"""Bölüm 18 laboratuvarı: tek yönlü ANOVA ve faktöriyel etkileşim."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def factorial_effects(cell_means: dict[tuple[int, int], float]) -> dict[str, float]:
    a_low = (cell_means[(-1, -1)] + cell_means[(-1, 1)]) / 2
    a_high = (cell_means[(1, -1)] + cell_means[(1, 1)]) / 2
    b_low = (cell_means[(-1, -1)] + cell_means[(1, -1)]) / 2
    b_high = (cell_means[(-1, 1)] + cell_means[(1, 1)]) / 2
    interaction = (
        cell_means[(1, 1)]
        - cell_means[(-1, 1)]
        - cell_means[(1, -1)]
        + cell_means[(-1, -1)]
    )
    return {"A ana etkisi": a_high - a_low, "B ana etkisi": b_high - b_low, "AB etkileşimi": interaction}


def main() -> None:
    groups = [
        np.array([410.0, 414.0, 416.0]),
        np.array([421.0, 419.0, 425.0]),
        np.array([430.0, 435.0, 432.0]),
    ]
    f_statistic, p_value = stats.f_oneway(*groups)
    grand_mean = np.concatenate(groups).mean()
    ss_between = sum(group.size * (group.mean() - grand_mean) ** 2 for group in groups)
    ss_error = sum(np.sum((group - group.mean()) ** 2) for group in groups)

    effects = factorial_effects({(-1, -1): 50, (1, -1): 58, (-1, 1): 54, (1, 1): 70})
    assert np.isclose(ss_between, 544.2222222222)
    assert np.isclose(ss_error, 50.0)
    assert np.isclose(f_statistic, 32.6533333333)
    assert effects == {"A ana etkisi": 12.0, "B ana etkisi": 8.0, "AB etkileşimi": 8}

    anova = pd.DataFrame(
        {
            "kaynak": ["sıcaklık", "hata"],
            "kareler_toplamı": [ss_between, ss_error],
            "serbestlik_derecesi": [2, 6],
            "ortalama_kare": [ss_between / 2, ss_error / 6],
        }
    )
    print(anova.round(4).to_string(index=False))
    print(f"\nF={f_statistic:.4f}, p={p_value:.6f}")
    print("Faktöriyel etkiler:", effects)


if __name__ == "__main__":
    main()
