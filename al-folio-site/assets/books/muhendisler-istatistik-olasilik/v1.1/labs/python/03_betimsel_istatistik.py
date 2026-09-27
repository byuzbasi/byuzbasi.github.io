"""Bölüm 3 laboratuvarı: betimsel istatistik ve veri kalite tanıları."""

import numpy as np


def descriptive_summary(values: np.ndarray) -> dict[str, float]:
    """Sonlu bir sayısal dizi için kitapta kullanılan özetleri döndürür."""
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or data.size < 2 or not np.isfinite(data).all():
        raise ValueError("En az iki sonlu gözlemden oluşan tek boyutlu dizi gerekir.")
    q1, median, q3 = np.quantile(data, [0.25, 0.50, 0.75])
    return {
        "n": float(data.size),
        "ortalama": float(data.mean()),
        "medyan": float(median),
        "orneklem_ss": float(data.std(ddof=1)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "cv_yuzde": float(100 * data.std(ddof=1) / data.mean()),
    }


def main() -> None:
    strength = np.array(
        [418, 421, 417, 425, 419, 422, 420, 438, 416, 424], dtype=float
    )
    summary = descriptive_summary(strength)
    assert np.isclose(summary["ortalama"], 422.0)
    assert np.isclose(summary["orneklem_ss"] ** 2, 40.0)

    clean = np.array([10.0, 10.1, 9.9, 10.2, 9.8])
    flagged = clean.copy()
    flagged[3] = 16.2
    comparison = {
        "temiz_ortalama": clean.mean(),
        "işaretli_ortalama": flagged.mean(),
        "temiz_medyan": np.median(clean),
        "işaretli_medyan": np.median(flagged),
    }

    for name, value in summary.items():
        unit = "adet" if name == "n" else ("%" if name == "cv_yuzde" else "MPa")
        print(f"{name}={value:.2f} {unit}")
    print("\nOlağan dışı kayıt duyarlılığı")
    for name, value in comparison.items():
        print(f"{name}={value:.2f} mm")


if __name__ == "__main__":
    main()
