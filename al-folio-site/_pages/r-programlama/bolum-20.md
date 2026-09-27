---
layout: page
title: "Bölüm 20 · Paket anatomisi ve metadata"
permalink: /r-programlama/bolum-20/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Metadata, paket hakkında çalıştırılabilir bir iddiadır
- DESCRIPTION: temel alanları okumak
- Bağımlılık türünü kullanım anı belirler
- Lisans alanı hukuki incelemenin özeti değildir
- NAMESPACE: kamusal yüzeyi dar tutmak
- Kaynak ağacındaki dosya sorumlulukları
- Bellek içi DCF laboratuvarı
- Ulusal üretim ile öğretim kapsamını ayırmak

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, knitr, testthat, roxygen2.

Bu komut Bölüm 18–24 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
PACKAGE_ENGINEERING_RUN_ID=okur-bolum-20-01 Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:PACKAGE_ENGINEERING_RUN_ID="okur-bolum-20-01"
Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [metadata_ve_ad_alani.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch20/metadata_ve_ad_alani.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 19](/r-programlama/bolum-19/) · [Dizin](/r-programlama/) · [Bölüm 21 →](/r-programlama/bolum-21/)
