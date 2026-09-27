"""Bölüm 11 laboratuvarı: örnekleme belirsizliği, bootstrap ve jackknife."""

from __future__ import annotations

import os
import numpy as np
import pandas as pd


def jackknife_standard_error(values: np.ndarray) -> float:
    """Ortanca için bırak-bir-dışarı jackknife standart hatası."""
    leave_one_out = np.array(
        [np.median(np.delete(values, index)) for index in range(values.size)]
    )
    return float(
        np.sqrt(
            (values.size - 1)
            / values.size
            * np.sum((leave_one_out - leave_one_out.mean()) ** 2)
        )
    )


def main() -> None:
    values = np.array([9.8, 10.1, 10.0, 10.4, 9.9, 10.2, 10.3, 11.0])
    rng = np.random.default_rng(202611)
    smoke = os.environ.get("BOOK_SMOKE") == "1"
    repetitions = 64 if smoke else 4_000
    print(f"{'SMOKE' if smoke else 'REFERENCE'}: {repetitions} tekrar")
    bootstrap = np.median(
        rng.choice(values, size=(repetitions, values.size), replace=True), axis=1
    )
    percentile_interval = np.quantile(bootstrap, [0.025, 0.975])
    bootstrap_se = float(bootstrap.std(ddof=1))
    jackknife_se = jackknife_standard_error(values)

    assert np.isclose(np.median(values), 10.15)
    assert np.isfinite(bootstrap_se) and bootstrap_se > 0
    assert values.min() <= percentile_interval[0] <= percentile_interval[1] <= values.max()
    if not smoke:
        assert np.isclose(bootstrap_se, 0.1306491184)
        assert np.allclose(percentile_interval, [9.9, 10.4])
    assert np.isclose(jackknife_se, 0.1322875656)

    table = pd.DataFrame(
        {
            "ölçü": [
                "örnek ortancası",
                "bootstrap standart hatası",
                "jackknife standart hatası",
                "%95 yüzdelik alt sınır",
                "%95 yüzdelik üst sınır",
            ],
            "değer_mm": [
                np.median(values),
                bootstrap_se,
                jackknife_se,
                percentile_interval[0],
                percentile_interval[1],
            ],
        }
    )
    print(table.round(4).to_string(index=False))
    print("\nYeniden örnekleme birimi bağımsız deney birimiyle eşleşmelidir.")


if __name__ == "__main__":
    main()
