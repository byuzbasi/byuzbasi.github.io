"""Bölüm 17 laboratuvarı: regresyon katsayıları, aralıklar ve etki tanısı."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm


def main() -> None:
    cycle = np.array([0, 50, 100, 150, 200, 250, 300, 350], dtype=float)
    loss = np.array([0.2, 1.0, 2.1, 3.3, 4.4, 4.8, 5.9, 7.2])
    design = sm.add_constant(cycle)
    fit = sm.OLS(loss, design).fit()
    prediction = fit.get_prediction(np.array([[1.0, 250.0]])).summary_frame(alpha=0.05)
    influence = fit.get_influence().summary_frame()

    assert np.allclose(fit.params, [0.1666666667, 0.0196904762])
    assert np.isclose(fit.rsquared, 0.9932008057)
    assert np.isclose(prediction.loc[0, "mean"], 5.0892857143)
    assert prediction.loc[0, "obs_ci_upper"] - prediction.loc[0, "obs_ci_lower"] > (
        prediction.loc[0, "mean_ci_upper"] - prediction.loc[0, "mean_ci_lower"]
    )

    coefficients = pd.DataFrame(
        {
            "terim": ["kesme", "çevrim"],
            "tahmin": fit.params,
            "standart_hata": fit.bse,
            "p_değeri": fit.pvalues,
        }
    )
    print(coefficients.round(6).to_string(index=False))
    print("\n250 çevrim aralıkları")
    print(prediction.round(4).to_string(index=False))
    print(f"\nEn büyük Cook uzaklığı: {influence['cooks_d'].max():.4f}")


if __name__ == "__main__":
    main()
