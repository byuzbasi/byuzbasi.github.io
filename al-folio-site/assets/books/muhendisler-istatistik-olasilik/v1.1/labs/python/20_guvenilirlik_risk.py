"""Bölüm 20 laboratuvarı: sistem güvenilirliği ve Kaplan-Meier hesabı."""

from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd


def k_out_of_n_reliability(k: int, n: int, reliability: float) -> float:
    if not 1 <= k <= n or not 0 <= reliability <= 1:
        raise ValueError("k, n ve güvenilirlik geçerli olmalıdır.")
    return sum(
        comb(n, working)
        * reliability**working
        * (1 - reliability) ** (n - working)
        for working in range(k, n + 1)
    )


def kaplan_meier_steps(
    failure_times: list[float],
    risk_sets: list[int],
    failures: list[int],
) -> pd.DataFrame:
    survival = 1.0
    rows: list[dict[str, float | int]] = []
    for time, at_risk, event_count in zip(failure_times, risk_sets, failures, strict=True):
        survival *= 1 - event_count / at_risk
        rows.append(
            {"zaman_saat": time, "risk_kümesi": at_risk, "arıza": event_count, "sağkalım": survival}
        )
    return pd.DataFrame(rows)


def main() -> None:
    sensor_reliability, controller_reliability = 0.95, 0.98
    parallel = 1 - (1 - sensor_reliability) ** 2
    system = parallel * controller_reliability
    two_of_three = k_out_of_n_reliability(2, 3, 0.9)
    km = kaplan_meier_steps([100, 200, 250], [6, 4, 3], [1, 1, 1])

    assert np.isclose(system, 0.97755)
    assert np.isclose(two_of_three, 0.972)
    assert np.allclose(km["sağkalım"], [5 / 6, 5 / 8, 5 / 12])

    print(km.round(4).to_string(index=False))
    print(f"\nParalel sensör + seri kontrol güvenilirliği: {system:.5f}")
    print(f"2-dan-3'e sistem güvenilirliği: {two_of_three:.5f}")


if __name__ == "__main__":
    main()
