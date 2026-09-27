---
layout: page
title: "Bölüm 24 · Kaynak paketi üretmek ve denetlemek"
permalink: /r-programlama/bolum-24/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Kontrol, kaynak klasöründe bir işlevi çalıştırmaktan fazlasıdır
- Beş paket durumu
- R CMD build: dağıtım sınırını üretmek
- R CMD INSTALL: temiz kurulum
- R CMD check: bütünleşik denetim
- ERROR, WARNING ve NOTE nasıl okunur?
- Geçici dosya ve süreç hijyeni
- Çoklu platform matrisi
- Yerel sürüm ile normatif sürümü ayırmak
- Sentetik günlük ile gerçek paket kontrolünü ayırmak
- Yayın adayı kontrol listesi

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, knitr, testthat, roxygen2.

Bu komut Bölüm 18–24 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
PACKAGE_ENGINEERING_RUN_ID=okur-bolum-24-01 Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:PACKAGE_ENGINEERING_RUN_ID="okur-bolum-24-01"
Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [paket_denetime_hazirlik.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch24/paket_denetime_hazirlik.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 23](/r-programlama/bolum-23/) · [Dizin](/r-programlama/) · [Bölüm 25 →](/r-programlama/bolum-25/)
