"""Bölüm 16 laboratuvarı: ki-kare hücre tanısı ve permütasyon testi."""

from __future__ import annotations

import os
import numpy as np
import pandas as pd
from scipy import stats


def monte_carlo_permutation_pvalue(
    first: np.ndarray,
    second: np.ndarray,
    repetitions: int = 9_999,
    seed: int = 202616,
) -> float:
    rng = np.random.default_rng(seed)
    observed = float(first.mean() - second.mean())
    pooled = np.concatenate([first, second])
    exceedances = 0
    for _ in range(repetitions):
        shuffled = rng.permutation(pooled)
        statistic = shuffled[: first.size].mean() - shuffled[first.size :].mean()
        exceedances += abs(statistic) >= abs(observed)
    return (1 + exceedances) / (repetitions + 1)


def main() -> None:
    table = np.array([[42, 18], [28, 32]])
    chi_square, p_value, degrees_freedom, expected = stats.chi2_contingency(
        table, correction=False
    )
    pearson_residuals = (table - expected) / np.sqrt(expected)
    cramer_v = np.sqrt(chi_square / table.sum())

    first = np.array([8.2, 8.5, 8.1, 9.0, 8.7])
    second = np.array([7.4, 7.8, 7.6, 8.0, 7.7])
    smoke = os.environ.get("BOOK_SMOKE") == "1"
    repetitions = 64 if smoke else 9_999
    print(f"{'SMOKE' if smoke else 'REFERENCE'}: {repetitions} tekrar")
    permutation_p = monte_carlo_permutation_pvalue(first, second, repetitions=repetitions)
    assert 1 / (repetitions + 1) <= permutation_p <= 1

    assert np.isclose(chi_square, 6.72)
    assert np.isclose(p_value, 0.0095337627)
    assert np.allclose(expected, [[35, 25], [35, 25]])
    assert np.isclose(cramer_v, 0.2366431913)

    cell_table = pd.DataFrame(
        {
            "hücre": ["hat1-alarm", "hat1-yok", "hat2-alarm", "hat2-yok"],
            "gözlenen": table.ravel(),
            "beklenen": expected.ravel(),
            "Pearson_artığı": pearson_residuals.ravel(),
            "X2_katkısı": ((table - expected) ** 2 / expected).ravel(),
        }
    )
    print(cell_table.round(4).to_string(index=False))
    print(f"\nX²={chi_square:.4f}, p={p_value:.4f}, Cramér V={cramer_v:.4f}")
    print(f"Monte Carlo permütasyon p-değeri={permutation_p:.4f}")


if __name__ == "__main__":
    main()
