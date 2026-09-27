"""Bölüm 10 laboratuvarı: limit teoremleri ve kısa Monte Carlo deneyi."""

from __future__ import annotations

import os
import numpy as np
import pandas as pd


def zero_event_upper_bound(repetitions: int, alpha: float = 0.05) -> float:
    if repetitions < 1 or not 0 < alpha < 1:
        raise ValueError("Tekrar sayısı ve alpha geçerli olmalıdır.")
    return 1 - alpha ** (1 / repetitions)


def main() -> None:
    rng = np.random.default_rng(20260906)
    smoke = os.environ.get("BOOK_SMOKE") == "1"
    repetitions = 64 if smoke else 20_000
    print(f"{'SMOKE' if smoke else 'REFERENCE'}: {repetitions} tekrar")
    components = rng.random((repetitions, 2)) < 0.98
    success = components.any(axis=1)
    estimate = float(success.mean())
    standard_error = float(np.sqrt(estimate * (1 - estimate) / repetitions))
    analytic = 1 - 0.02**2

    exact_upper = zero_event_upper_bound(1000)
    rule_of_three = 3 / 1000
    assert np.isclose(analytic, 0.9996)
    assert np.isclose(exact_upper, 0.0029912495)

    table = pd.DataFrame(
        {
            "ölçü": [
                "analitik güvenilirlik",
                "Monte Carlo güvenilirliği",
                "Monte Carlo standart hatası",
                "1000 sıfır arızada kesin üst sınır",
                "1000 sıfır arızada üç kuralı",
            ],
            "değer": [
                analytic,
                estimate,
                standard_error,
                exact_upper,
                rule_of_three,
            ],
        }
    )
    print(table.round(7).to_string(index=False))
    print("\nSmoketest yalnız kod yolunu sınar; referans sonuç veya fiziksel model doğrulaması değildir.")


if __name__ == "__main__":
    main()
