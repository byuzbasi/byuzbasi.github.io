"""Bölüm 9 laboratuvarı: ortak değişkenlik ve hata yayılımı."""

from __future__ import annotations

import numpy as np
import pandas as pd


def total_variance(
    probabilities: np.ndarray,
    conditional_means: np.ndarray,
    conditional_variances: np.ndarray,
) -> tuple[float, float, float]:
    probabilities = np.asarray(probabilities, dtype=float)
    if not np.isclose(probabilities.sum(), 1.0) or (probabilities < 0).any():
        raise ValueError("Koşul olasılıkları geçerli olmalıdır.")
    overall_mean = float(probabilities @ conditional_means)
    within = float(probabilities @ conditional_variances)
    between = float(probabilities @ (conditional_means - overall_mean) ** 2)
    return overall_mean, within, between


def main() -> None:
    mean_mpa, within_mpa2, between_mpa2 = total_variance(
        np.array([0.5, 0.5]),
        np.array([100.0, 106.0]),
        np.array([4.0, 4.0]),
    )
    covariance = np.array([[0.8**2, 0.48], [0.48, 1.2**2]])
    weights = np.array([0.5, 0.5])
    combined_variance = float(weights @ covariance @ weights)
    eigenvalues = np.linalg.eigvalsh(covariance)

    assert np.isclose(mean_mpa, 103.0)
    assert np.isclose(within_mpa2 + between_mpa2, 13.0)
    assert np.isclose(combined_variance, 0.76)
    assert (eigenvalues >= -1e-12).all()

    print(
        pd.DataFrame(
            {
                "ölçü": [
                    "genel ortalama (MPa)",
                    "vardiya içi varyans (MPa^2)",
                    "vardiyalar arası varyans (MPa^2)",
                    "toplam varyans (MPa^2)",
                    "iki sensör ortalamasının varyansı (°C^2)",
                ],
                "değer": [
                    mean_mpa,
                    within_mpa2,
                    between_mpa2,
                    within_mpa2 + between_mpa2,
                    combined_variance,
                ],
            }
        ).round(4).to_string(index=False)
    )
    print(f"\nKovaryans matrisi özdeğerleri: {np.round(eigenvalues, 6)}")


if __name__ == "__main__":
    main()
