"""Bölüm 4 laboratuvarı: olay cebiri, dahil etme-dışlama ve tam sayım."""

from __future__ import annotations

from itertools import product
from math import comb, isclose

import pandas as pd


def three_event_union(
    p_a: float,
    p_b: float,
    p_c: float,
    p_ab: float,
    p_ac: float,
    p_bc: float,
    p_abc: float,
) -> float:
    """Üç olay için dahil etme-dışlama olasılığını hesaplar."""
    values = (p_a, p_b, p_c, p_ab, p_ac, p_bc, p_abc)
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("Bütün olasılıklar 0 ile 1 arasında olmalıdır.")
    result = p_a + p_b + p_c - p_ab - p_ac - p_bc + p_abc
    if not 0 <= result <= 1:
        raise ValueError("Girilen olasılıklar tutarlı bir birleşim üretmiyor.")
    return result


def main() -> None:
    states = pd.DataFrame(product([0, 1], repeat=3), columns=["S1", "S2", "S3"])
    states["alarm_sayısı"] = states.sum(axis=1)
    summary = pd.DataFrame(
        {
            "olay": ["hiç alarm yok", "tam bir alarm", "en az iki alarm"],
            "durum_sayısı": [
                (states["alarm_sayısı"] == 0).sum(),
                (states["alarm_sayısı"] == 1).sum(),
                (states["alarm_sayısı"] >= 2).sum(),
            ],
        }
    )
    summary["eş_olasılıklı_olasılık"] = summary["durum_sayısı"] / len(states)

    union = three_event_union(0.10, 0.07, 0.05, 0.02, 0.01, 0.015, 0.005)
    assert isclose(union, 0.18, abs_tol=1e-12)
    assert comb(8, 3) == 56

    print(summary.to_string(index=False))
    print(f"\nÜç arıza yolundan en az biri: {union:.3f}")
    print(f"Sekiz adaydan üç sırasız sensör seçimi: {comb(8, 3)}")


if __name__ == "__main__":
    main()
