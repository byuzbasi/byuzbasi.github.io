"""Bölüm 7 laboratuvarı: kesikli dağılım seçimi ve kuyruk hesapları."""

from __future__ import annotations

from math import comb
import os

import numpy as np
import pandas as pd
from scipy import stats


def main() -> None:
    binomial_tail = stats.binom.sf(0, n=20, p=0.02)
    hyper_no_defect = stats.hypergeom.pmf(0, M=100, n=8, N=10)
    binomial_approx = stats.binom.pmf(0, n=10, p=0.08)
    poisson_at_most_four = stats.poisson.cdf(4, mu=6)

    assert np.isclose(binomial_tail, 1 - 0.98**20)
    assert np.isclose(hyper_no_defect, comb(92, 10) / comb(100, 10))
    assert np.isclose(hyper_no_defect, 0.41655327299)

    rng = np.random.default_rng(202607)
    multinomial_counts = rng.multinomial(
        n=200, pvals=[0.90, 0.06, 0.04],
        size=64 if os.environ.get("BOOK_SMOKE") == "1" else 1000
    )
    multinomial_means = multinomial_counts.mean(axis=0)

    table = pd.DataFrame(
        {
            "hesap": [
                "20 kartta en az bir kusur",
                "100 parçadan 10 seçimde sıfır kusur",
                "aynı soruda binom yaklaşımı",
                "iki saatte en çok dört arıza",
            ],
            "olasılık": [
                binomial_tail,
                hyper_no_defect,
                binomial_approx,
                poisson_at_most_four,
            ],
        }
    )
    print(table.round(5).to_string(index=False))
    print("\nMultinom sayım ortalamaları (sağlam, yüzey, boyut)")
    print(np.round(multinomial_means, 2))


if __name__ == "__main__":
    main()
