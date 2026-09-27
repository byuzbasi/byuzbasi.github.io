"""Bölüm 22 laboratuvarı: asimetrik karar kaybı ve salt-okunur manifest."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd


def expected_capacity_loss(
    capacity: float,
    demand: np.ndarray,
    probabilities: np.ndarray,
    shortage_cost: float,
    surplus_cost: float,
) -> float:
    if not np.isclose(probabilities.sum(), 1) or np.any(probabilities < 0):
        raise ValueError("Olasılıklar negatif olmamalı ve toplamları bir olmalıdır.")
    shortage = np.maximum(demand - capacity, 0)
    surplus = np.maximum(capacity - demand, 0)
    return float(probabilities @ (shortage_cost * shortage + surplus_cost * surplus))


def readonly_manifest(path: Path) -> dict[str, str | int | None]:
    if not path.exists():
        return {"dosya": str(path), "bayt": None, "sha256": "dosya_yok"}
    payload = path.read_bytes()
    return {"dosya": str(path), "bayt": len(payload), "sha256": sha256(payload).hexdigest()}


def main() -> None:
    demand = np.array([90.0, 100.0, 120.0])
    probabilities = np.array([0.2, 0.5, 0.3])
    capacities = np.array([105.0, 115.0, 120.0])
    losses = np.array(
        [expected_capacity_loss(q, demand, probabilities, 1000, 100) for q in capacities]
    )
    assert np.allclose(losses, [5050, 2750, 1600])
    assert capacities[np.argmin(losses)] == 120

    decisions = pd.DataFrame({"kapasite_MW": capacities, "beklenen_kayıp_TL": losses})
    print(decisions.to_string(index=False))
    manifest = readonly_manifest(Path("tables/generated/v1/pilot_summary.csv"))
    print("\nSalt-okunur manifest denetimi:")
    print(pd.DataFrame([manifest]).to_string(index=False))


if __name__ == "__main__":
    main()
