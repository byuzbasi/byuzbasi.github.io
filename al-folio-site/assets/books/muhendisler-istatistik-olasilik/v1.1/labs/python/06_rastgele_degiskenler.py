"""Bölüm 6 laboratuvarı: rastgele değişkenler, momentler ve yüzdelikler."""

from __future__ import annotations

import numpy as np
import pandas as pd


def validate_pmf(values: np.ndarray, probabilities: np.ndarray) -> None:
    if values.ndim != 1 or probabilities.ndim != 1 or values.size != probabilities.size:
        raise ValueError("Değer ve olasılık dizileri aynı uzunlukta olmalıdır.")
    if not np.isfinite(values).all() or not np.isfinite(probabilities).all():
        raise ValueError("Bütün girdiler sonlu olmalıdır.")
    if (probabilities < 0).any() or not np.isclose(probabilities.sum(), 1.0):
        raise ValueError("Olasılıklar negatif olamaz ve toplamları 1 olmalıdır.")


def discrete_quantile(
    values: np.ndarray, probabilities: np.ndarray, probability_level: float
) -> float:
    validate_pmf(values, probabilities)
    if not 0 < probability_level < 1:
        raise ValueError("Yüzdelik düzeyi 0 ile 1 arasında açık olmalıdır.")
    order = np.argsort(values)
    ordered_values = values[order]
    cumulative = np.cumsum(probabilities[order])
    return float(ordered_values[np.searchsorted(cumulative, probability_level)])


def main() -> None:
    load_kN = np.array([0.0, 2.0, 5.0])
    probability = np.array([0.6, 0.3, 0.1])
    validate_pmf(load_kN, probability)
    mean_load = float(np.sum(load_kN * probability))
    variance_load = float(np.sum((load_kN - mean_load) ** 2 * probability))
    q95 = discrete_quantile(load_kN, probability, 0.95)

    speed = np.array([10.0, 20.0, 30.0])
    speed_probability = np.array([0.5, 0.3, 0.2])
    kinetic_energy = speed**2  # m=2 kg için m*v^2/2 = v^2 joule
    expected_energy = float(np.sum(kinetic_energy * speed_probability))
    energy_at_expected_speed = float(np.sum(speed * speed_probability) ** 2)
    entropy_bits = float(-np.sum(probability * np.log2(probability)))

    assert np.isclose(mean_load, 1.1)
    assert np.isclose(variance_load, 2.49)
    assert q95 == 5.0
    assert np.isclose(expected_energy, 350.0)
    assert np.isclose(energy_at_expected_speed, 289.0)

    print(
        pd.DataFrame(
            {
                "ölçü": [
                    "beklenen yük (kN)",
                    "yük varyansı (kN^2)",
                    "yük yüzde 95 (kN)",
                    "beklenen enerji (J)",
                    "ortalama hızdaki enerji (J)",
                    "yük entropisi (bit)",
                ],
                "değer": [
                    mean_load,
                    variance_load,
                    q95,
                    expected_energy,
                    energy_at_expected_speed,
                    entropy_bits,
                ],
            }
        ).round(4).to_string(index=False)
    )


if __name__ == "__main__":
    main()
