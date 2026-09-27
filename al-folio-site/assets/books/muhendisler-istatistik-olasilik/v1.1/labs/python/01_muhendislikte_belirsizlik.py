"""Bölüm 1 laboratuvarı: belirsizlik, beklenen kayıp ve duyarlılık."""

from __future__ import annotations

import numpy as np
import pandas as pd


def expected_total_loss(
    direct_cost_tl: float,
    failure_probability: float,
    failure_loss_tl: float,
) -> float:
    """Doğrudan maliyet ile beklenen arıza kaybını aynı TL ölçeğinde toplar."""
    if direct_cost_tl < 0 or failure_loss_tl < 0:
        raise ValueError("Maliyetler negatif olamaz.")
    if not 0 <= failure_probability <= 1:
        raise ValueError("Arıza olasılığı 0 ile 1 arasında olmalıdır.")
    return direct_cost_tl + failure_probability * failure_loss_tl


def main() -> None:
    designs = pd.DataFrame(
        {
            "tasarım": ["standart", "yedekli"],
            "doğrudan_maliyet_tl": [0.0, 2500.0],
            "arıza_olasılığı": [0.004, 0.0002],
            "arıza_kaybı_tl": [1_000_000.0, 1_000_000.0],
        }
    )
    designs["beklenen_toplam_kayıp_tl"] = [
        expected_total_loss(cost, probability, loss)
        for cost, probability, loss in zip(
            designs["doğrudan_maliyet_tl"],
            designs["arıza_olasılığı"],
            designs["arıza_kaybı_tl"],
        )
    ]

    break_even_cost = (
        designs.loc[0, "arıza_olasılığı"] - designs.loc[1, "arıza_olasılığı"]
    ) * designs.loc[0, "arıza_kaybı_tl"]
    assert np.isclose(break_even_cost, 3800.0)
    assert designs.loc[1, "beklenen_toplam_kayıp_tl"] < designs.loc[
        0, "beklenen_toplam_kayıp_tl"
    ]

    sensitivity = pd.DataFrame(
        {
            "arıza_kaybı_tl": [250_000.0, 500_000.0, 1_000_000.0, 2_000_000.0]
        }
    )
    sensitivity["başabaş_maliyet_tl"] = (
        0.004 - 0.0002
    ) * sensitivity["arıza_kaybı_tl"]

    print("Beklenen kayıp karşılaştırması")
    print(designs.to_string(index=False))
    print("\nArıza kaybına göre başabaş maliyeti")
    print(sensitivity.to_string(index=False))
    print("\nNot: Güvenlik ve etik kısıtlar parasal beklentiden ayrı değerlendirilir.")


if __name__ == "__main__":
    main()
