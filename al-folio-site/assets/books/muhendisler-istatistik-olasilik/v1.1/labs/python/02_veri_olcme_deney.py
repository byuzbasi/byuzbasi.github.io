"""Bölüm 2 laboratuvarı: kalibrasyon, belirsizlik yayılımı ve örnekleme."""

from __future__ import annotations

import numpy as np
import pandas as pd


def corrected_value(observed: float, slope: float, intercept: float) -> float:
    """X = a*theta + b kalibrasyon modelini theta için çözer."""
    if slope == 0:
        raise ValueError("Kalibrasyon eğimi sıfır olamaz.")
    return (observed - intercept) / slope


def rectangle_area_uncertainty(
    length_mm: float,
    width_mm: float,
    u_length_mm: float,
    u_width_mm: float,
) -> tuple[float, float]:
    """Bağımsız küçük belirsizlikler için alan ve birleşik standart belirsizlik."""
    values = (length_mm, width_mm, u_length_mm, u_width_mm)
    if any(value <= 0 for value in values):
        raise ValueError("Uzunluklar ve standart belirsizlikler pozitif olmalıdır.")
    area = length_mm * width_mm
    combined = np.sqrt(
        (width_mm * u_length_mm) ** 2 + (length_mm * u_width_mm) ** 2
    )
    return area, combined


def main() -> None:
    corrected = corrected_value(observed=10.7, slope=1.02, intercept=-0.5)
    area, u_area = rectangle_area_uncertainty(120.0, 80.0, 0.2, 0.1)
    assert np.isclose(corrected, 10.980392156862745)
    assert np.isclose(area, 9600.0)
    assert np.isclose(u_area, 20.0)

    rng = np.random.default_rng(202602)
    day = rng.normal(48.0, 3.0, 5000)
    night = rng.normal(56.0, 4.0, 5000)
    population = np.concatenate([day, night])
    simple_random = rng.choice(population, size=400, replace=False)
    convenience = rng.choice(day, size=400, replace=False)

    summary = pd.DataFrame(
        {
            "kaynak": ["anakütle", "basit rastgele", "yalnız gündüz"],
            "n": [population.size, simple_random.size, convenience.size],
            "ortalama_kwh_urun": [
                population.mean(),
                simple_random.mean(),
                convenience.mean(),
            ],
        }
    )

    print(f"Düzeltilmiş değer: {corrected:.3f} V")
    print(f"Alan: {area:.1f} mm^2; standart belirsizlik: {u_area:.1f} mm^2")
    print("\nÖrnekleme karşılaştırması")
    print(summary.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
