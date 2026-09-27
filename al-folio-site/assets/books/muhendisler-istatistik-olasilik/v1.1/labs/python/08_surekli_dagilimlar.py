"""Bölüm 8 laboratuvarı: sürekli dağılımlar, yüzdelikler ve kuyruklar."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def main() -> None:
    p_in_spec = stats.norm.cdf(20.06, loc=20.0, scale=0.04) - stats.norm.cdf(
        19.94, loc=20.0, scale=0.04
    )
    weibull_survival = stats.weibull_min.sf(1500, c=1.8, scale=2000)

    median_ms = 100.0
    sigma_log = 0.4
    mu_log = np.log(median_ms)
    lognormal_mean = np.exp(mu_log + sigma_log**2 / 2)
    lognormal_q95 = stats.lognorm.ppf(
        0.95, s=sigma_log, scale=np.exp(mu_log)
    )

    assert np.isclose(p_in_spec, 0.8663855975)
    assert np.isclose(lognormal_mean, 108.32870677)
    assert np.isclose(lognormal_q95, 193.0813566)

    table = pd.DataFrame(
        {
            "hesap": [
                "normal şartname olasılığı",
                "Weibull 1500 saat sağkalımı",
                "lognormal ortalama (ms)",
                "lognormal yüzde 95 (ms)",
            ],
            "değer": [
                p_in_spec,
                weibull_survival,
                lognormal_mean,
                lognormal_q95,
            ],
        }
    )
    print(table.round(5).to_string(index=False))
    print("\nKuyruk hesabında çok küçük olasılıklar için sf kullanılır.")


if __name__ == "__main__":
    main()
