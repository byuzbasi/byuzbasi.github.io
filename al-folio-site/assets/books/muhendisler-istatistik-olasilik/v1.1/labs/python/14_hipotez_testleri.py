"""Bölüm 14 laboratuvarı: tek örneklem testi, güç ve eşdeğerlik."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def known_sigma_left_power(
    null_mean: float,
    true_mean: float,
    sigma: float,
    sample_size: int,
    alpha: float = 0.05,
) -> float:
    standard_error = sigma / np.sqrt(sample_size)
    critical_mean = null_mean + stats.norm.ppf(alpha) * standard_error
    return float(stats.norm.cdf((critical_mean - true_mean) / standard_error))


def main() -> None:
    sample_size, mean, standard_deviation, null_mean = 16, 96.0, 8.0, 100.0
    standard_error = standard_deviation / np.sqrt(sample_size)
    t_observed = (mean - null_mean) / standard_error
    p_left = stats.t.cdf(t_observed, df=sample_size - 1)
    t_value = stats.t.ppf(0.975, df=sample_size - 1)
    difference_interval = mean - null_mean + np.array([-1, 1]) * t_value * standard_error

    power = known_sigma_left_power(100.0, 97.0, 6.0, 36)
    equivalence_interval = np.array([-0.8, 0.3])
    equivalent_at_one = bool(np.all(equivalence_interval > -1) and np.all(equivalence_interval < 1))
    equivalent_at_half = bool(np.all(equivalence_interval > -0.5) and np.all(equivalence_interval < 0.5))

    assert np.isclose(t_observed, -2.0)
    assert np.isclose(power, 0.9123145368)
    assert equivalent_at_one and not equivalent_at_half

    table = pd.DataFrame(
        {
            "ölçü": [
                "t istatistiği",
                "sol yönlü p-değeri",
                "fark aralığı alt",
                "fark aralığı üst",
                "3 kWh azalma için güç",
            ],
            "değer": [t_observed, p_left, difference_interval[0], difference_interval[1], power],
        }
    )
    print(table.round(4).to_string(index=False))
    print(f"\n±1 kWh eşdeğer: {equivalent_at_one}; ±0.5 kWh eşdeğer: {equivalent_at_half}")


if __name__ == "__main__":
    main()
