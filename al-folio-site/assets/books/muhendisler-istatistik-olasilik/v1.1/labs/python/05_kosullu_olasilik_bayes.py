"""Bölüm 5 laboratuvarı: Bayes güncellemesi ve sistem güvenilirliği."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "python"))

from bookstats import parallel_reliability, posterior_defect, series_reliability


def posterior_after_positive_tests(
    prior: float,
    sensitivity: float,
    specificity: float,
    positive_tests: int,
) -> float:
    """Koşullu bağımsız pozitif testler için odds güncellemesi yapar."""
    if not 0 < prior < 1:
        raise ValueError("Önsel olasılık 0 ile 1 arasında açık olmalıdır.")
    if not 0 < sensitivity <= 1 or not 0 <= specificity < 1:
        raise ValueError("Test olasılıklarını denetleyin.")
    if positive_tests < 1:
        raise ValueError("En az bir pozitif test gerekir.")
    prior_odds = prior / (1 - prior)
    likelihood_ratio = sensitivity / (1 - specificity)
    posterior_odds = prior_odds * likelihood_ratio**positive_tests
    return posterior_odds / (1 + posterior_odds)


def main() -> None:
    one_test = posterior_defect(0.01, 0.95, 0.98)
    two_tests = posterior_after_positive_tests(0.01, 0.95, 0.98, 2)
    assert np.isclose(one_test, 0.3242320819)
    assert np.isclose(two_tests, 0.9579662456)

    base_rates = np.array([0.001, 0.005, 0.01, 0.05, 0.10])
    table = pd.DataFrame(
        {
            "temel_oran": base_rates,
            "tek_alarm_sonrası": [
                posterior_defect(rate, 0.95, 0.98) for rate in base_rates
            ],
            "iki_alarm_sonrası": [
                posterior_after_positive_tests(rate, 0.95, 0.98, 2)
                for rate in base_rates
            ],
        }
    )

    print(table.round(4).to_string(index=False))
    print(f"\nSeri sistem: {series_reliability([0.98, 0.97]):.4f}")
    print(f"Paralel sistem: {parallel_reliability([0.98, 0.98]):.4f}")
    print("İki-test hesabı, durum verildiğinde koşullu bağımsızlık varsayar.")


if __name__ == "__main__":
    main()
