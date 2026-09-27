"""Bölüm 21 laboratuvarı: AR(1) öngörüsü ve Markov durumları."""

from __future__ import annotations

import numpy as np
import pandas as pd


def ar1_forecasts(constant: float, phi: float, last_value: float, horizons: np.ndarray) -> np.ndarray:
    if abs(phi) >= 1:
        raise ValueError("Bu durağan AR(1) hesabı |phi| < 1 gerektirir.")
    long_run_mean = constant / (1 - phi)
    return long_run_mean + phi**horizons * (last_value - long_run_mean)


def stationary_distribution(transition: np.ndarray) -> np.ndarray:
    if np.any(transition < 0) or not np.allclose(transition.sum(axis=1), 1):
        raise ValueError("Geçiş matrisi olasılık satırlarından oluşmalıdır.")
    coefficients = np.vstack([transition.T - np.eye(transition.shape[0]), np.ones(transition.shape[0])])
    target = np.append(np.zeros(transition.shape[0]), 1)
    solution, *_ = np.linalg.lstsq(coefficients, target, rcond=None)
    return solution


def main() -> None:
    horizons = np.arange(1, 5)
    forecasts = ar1_forecasts(20, 0.7, 80, horizons)
    transition = np.array(
        [[0.90, 0.08, 0.02], [0.55, 0.40, 0.05], [0.35, 0.15, 0.50]]
    )
    initial = np.array([1.0, 0.0, 0.0])
    after_five = initial @ np.linalg.matrix_power(transition, 5)
    stationary = stationary_distribution(transition)

    assert np.allclose(forecasts, [76.0, 73.2, 71.24, 69.868])
    assert np.allclose(after_five, [0.834904875, 0.121332075, 0.04376305])
    assert np.allclose(stationary, [0.83214794, 0.12233286, 0.04551920], atol=1e-8)

    print(pd.DataFrame({"ufuk_saat": horizons, "öngörü_MW": forecasts}).round(3).to_string(index=False))
    print("\n5 adım dağılımı:", np.round(after_five, 4))
    print("Durağan dağılım:", np.round(stationary, 4))


if __name__ == "__main__":
    main()
