"""Bölüm 19 laboratuvarı: kontrol sinyalleri ve yeterlilik duyarlılığı."""

from __future__ import annotations

import numpy as np
import pandas as pd


def capability(lsl: float, usl: float, mean: float, sigma: float) -> tuple[float, float]:
    if not lsl < usl or sigma <= 0:
        raise ValueError("Şartname sınırları ve sigma geçerli olmalıdır.")
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
    return cp, cpk


def main() -> None:
    subgroup_means = np.array([500.4, 499.1, 501.2, 498.8, 502.0, 507.0, 500.1, 499.7])
    process_mean, process_sigma, subgroup_size = 500.0, 4.0, 4
    lower = process_mean - 3 * process_sigma / np.sqrt(subgroup_size)
    upper = process_mean + 3 * process_sigma / np.sqrt(subgroup_size)
    signals = (subgroup_means < lower) | (subgroup_means > upper)

    cp_shifted, cpk_shifted = capability(9.5, 10.5, 10.1, 0.1)
    cp_centered, cpk_centered = capability(9.5, 10.5, 10.0, 0.1)
    assert (lower, upper) == (494.0, 506.0)
    assert signals.tolist() == [False, False, False, False, False, True, False, False]
    assert np.isclose(cp_shifted, 5 / 3)
    assert np.isclose(cpk_shifted, 4 / 3)
    assert np.isclose(cp_centered, cpk_centered)

    chart = pd.DataFrame(
        {
            "alt_grup": np.arange(1, subgroup_means.size + 1),
            "ortalama_mL": subgroup_means,
            "LCL_mL": lower,
            "UCL_mL": upper,
            "sinyal": signals,
        }
    )
    print(chart.to_string(index=False))
    print(
        "\nYeterlilik:",
        {"kaymış Cp": round(cp_shifted, 4), "kaymış Cpk": round(cpk_shifted, 4), "merkezli Cpk": round(cpk_centered, 4)},
    )


if __name__ == "__main__":
    main()
