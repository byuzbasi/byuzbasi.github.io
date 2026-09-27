"""Bölüm 13 laboratuvarı: güven, öngörü ve Wilson aralıkları."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def wilson_interval(events: int, sample_size: int, alpha: float = 0.05) -> tuple[float, float]:
    if not 0 <= events <= sample_size or sample_size < 1:
        raise ValueError("Olay ve örneklem sayıları geçerli olmalıdır.")
    proportion = events / sample_size
    z_value = stats.norm.ppf(1 - alpha / 2)
    denominator = 1 + z_value**2 / sample_size
    center = (proportion + z_value**2 / (2 * sample_size)) / denominator
    half_width = z_value / denominator * np.sqrt(
        proportion * (1 - proportion) / sample_size
        + z_value**2 / (4 * sample_size**2)
    )
    return float(center - half_width), float(center + half_width)


def main() -> None:
    sample_size, mean, standard_deviation = 16, 52.4, 2.8
    t_value = stats.t.ppf(0.975, df=sample_size - 1)
    confidence = mean + np.array([-1, 1]) * t_value * standard_deviation / np.sqrt(sample_size)
    prediction = mean + np.array([-1, 1]) * t_value * standard_deviation * np.sqrt(
        1 + 1 / sample_size
    )
    wilson = wilson_interval(events=6, sample_size=80)
    planned_n = int(np.ceil((stats.norm.ppf(0.975) * 4 / 1) ** 2))

    assert np.allclose(wilson, [0.0348252493, 0.1541201608])
    assert planned_n == 62
    assert prediction[1] - prediction[0] > confidence[1] - confidence[0]

    table = pd.DataFrame(
        {
            "aralık": ["ortalama güven", "tek gözlem öngörü", "kusur oranı Wilson"],
            "alt": [confidence[0], prediction[0], wilson[0]],
            "üst": [confidence[1], prediction[1], wilson[1]],
        }
    )
    print(table.round(4).to_string(index=False))
    print(f"\nPlanlanan örneklem büyüklüğü: {planned_n}")


if __name__ == "__main__":
    main()
