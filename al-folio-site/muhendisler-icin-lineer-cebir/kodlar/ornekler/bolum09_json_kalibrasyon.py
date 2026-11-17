"""Bölüm 9: JSON verisini mevcut QR yordamıyla yük hücresi modeline uydur.

Model: y = beta_0 + beta_F * F + beta_T * delta_T + artık.
F: N, delta_T: K, y: mV. Bu örnek ağırlıksız en küçük kareler kullanır.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

# Dosya konumuna göre çözümleme, çalışma klasöründen bağımsız çalışmayı sağlar.
PAKET_KOKU = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAKET_KOKU / "python" / "applications" / "python"))
from bolum09_en_kucuk_kareler import (  # noqa: E402
    lstsq_reference,
    qr_least_squares,
    scaled_calibration_design,
    scaled_to_physical_coefficients,
)


def hesapla(veri_yolu: Path, *, kitap_kontrolu: bool = False) -> dict:
    """Dosyayı oku, çöz, katsayıları fiziksel birimlere dönüştür ve karşılaştır."""
    with veri_yolu.open(encoding="utf-8") as dosya:
        veri = json.load(dosya)["ornekler"]["yuk_hucresi"]

    # A'nın sütunları 1, F/s_F ve delta_T/s_T'dir; ölçekler JSON'dan alınır.
    olcekler = {
        "force_scale_newton": veri["force_scale_newton"],
        "temperature_scale_kelvin": veri["temperature_scale_kelvin"],
    }
    a = scaled_calibration_design(
        veri["force_newton"], veri["temperature_change_kelvin"], **olcekler
    )
    y = np.asarray(veri["response_millivolt"], dtype=float)
    sonuc = qr_least_squares(a, y)
    beta = scaled_to_physical_coefficients(sonuc.solution, **olcekler)

    # İkinci kitaplık yordamıyla karşılaştırma ve A^T r kontrolü ayrı kanıtlardır.
    referans = lstsq_reference(a, y)
    katsayi_farki = float(np.linalg.norm(sonuc.solution - referans["solution"], np.inf))

    # Kontrol ölçümü katsayı kestirimine KATILMAZ: yalnız yeni tahmini sınar.
    kontrol = veri["check"]
    kontrol_a = scaled_calibration_design(
        [kontrol["force_newton"]], [kontrol["temperature_change_kelvin"]], **olcekler
    )
    gozlenen = float(kontrol["observed_response_millivolt"])
    if not np.isfinite(gozlenen):
        raise ValueError("Kontrol ölçümünün yanıtı sonlu olmalıdır.")
    tahmin = float((kontrol_a @ sonuc.solution)[0])

    rapor = {
        "yöntem": "Ağırlıksız en küçük kareler; ince QR",
        "ölçüm_sayısı": int(a.shape[0]),
        "tasarım_rankı": sonuc.rank,
        "ölçekli_katsayılar": sonuc.solution.tolist(),
        "fiziksel_katsayılar": {
            "sabit_mV": float(beta[0]),
            "kuvvet_mV_N": float(beta[1]),
            "sıcaklık_mV_K": float(beta[2]),
        },
        "artık_kareler_toplamı_mV2": sonuc.residual_sum_squares,
        "ölçekli_tasarım_koşul_sayısı": sonuc.condition_2,
        "QR_ile_lstsq_katsayı_farkı_inf": katsayi_farki,
        "A_transpoz_artık_inf": sonuc.normal_equation_residual_inf,
        "ölçeklendirilmiş_durağanlık_artığı": sonuc.normal_equation_residual_relative,
        "kontrol_tahmini_mV": tahmin,
        "kontrol_artığı_mV": gozlenen - tahmin,
    }
    if kitap_kontrolu:
        # Bu sabit beklentiler yalnız değiştirilmemiş kitap girdisi içindir.
        np.testing.assert_allclose(beta, [0.2, 0.004, 0.01], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(sonuc.residual_sum_squares, 0.0022, atol=1e-12, rtol=0)
        np.testing.assert_allclose(tahmin, 2.72, atol=1e-12, rtol=0)
        np.testing.assert_allclose(sonuc.solution, referans["solution"], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(a.T @ sonuc.residual, 0.0, atol=1e-12, rtol=0)
        rapor["kitap_sonuç_kontrolü"] = "GEÇTİ"
    return rapor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--veri", type=Path, default=PAKET_KOKU / "veriler" / "bolum-09.json",
                        help="Yük hücresi JSON dosyası; göreli yol çalışma klasöründen çözülür.")
    parser.add_argument("--kitap-kontrolu", action="store_true",
                        help="Değiştirilmemiş kitap verisinin bilinen sonuçlarını doğrula.")
    args = parser.parse_args()
    try:
        rapor = hesapla(args.veri, kitap_kontrolu=args.kitap_kontrolu)
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as hata:
        print(f"Veri veya sonuç kontrolü başarısız: {hata}", file=sys.stderr)
        return 2
    print(json.dumps(rapor, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
