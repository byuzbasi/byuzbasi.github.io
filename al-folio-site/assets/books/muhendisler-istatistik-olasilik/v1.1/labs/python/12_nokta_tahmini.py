"""Bölüm 12 laboratuvarı: maksimum olabilirlik ve sağlamlık duyarlılığı."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import trim_mean


def exponential_negative_loglik(rate: float, lifetimes: np.ndarray) -> float:
    if rate <= 0:
        return np.inf
    return float(-(lifetimes.size * np.log(rate) - rate * lifetimes.sum()))


def main() -> None:
    lifetimes = np.array([82.0, 105.0, 97.0, 121.0, 76.0, 110.0])
    analytic_rate = 1 / lifetimes.mean()
    fit = minimize_scalar(
        exponential_negative_loglik,
        args=(lifetimes,),
        bounds=(1e-6, 0.2),
        method="bounded",
    )

    defect_count, sample_size = 18, 50
    bernoulli_mle = defect_count / sample_size
    bernoulli_se = np.sqrt(bernoulli_mle * (1 - bernoulli_mle) / sample_size)

    contaminated = np.append(lifetimes, 800.0)
    sensitivity = pd.DataFrame(
        {
            "veri": ["özgün", "800 saat eklenmiş"],
            "ortalama_saat": [lifetimes.mean(), contaminated.mean()],
            "yüzde20_kırpılmış_ortalama": [
                trim_mean(lifetimes, 0.20),
                trim_mean(contaminated, 0.20),
            ],
        }
    )

    assert fit.success
    assert np.isclose(fit.x, analytic_rate, atol=1e-6)
    assert np.isclose(bernoulli_mle, 0.36)
    assert np.isclose(bernoulli_se, 0.06788225099)

    results = pd.DataFrame(
        {
            "tahmin": ["analitik üstel hız", "sayısal üstel hız", "kusur olasılığı"],
            "değer": [analytic_rate, fit.x, bernoulli_mle],
        }
    )
    print(results.round(6).to_string(index=False))
    print("\nDuyarlılık özeti")
    print(sensitivity.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
