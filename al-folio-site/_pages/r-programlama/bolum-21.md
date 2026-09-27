---
layout: page
title: "Bölüm 21 · Belgeleme ve örnekler"
permalink: /r-programlama/bolum-21/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Belge, API sözleşmesinin kullanıcı yüzüdür
- Bir yardım sayfasının soruları
- Roxygen2 kaynak açıklamasını okumak
- Kaynak ile üretilmiş belge arasında iz
- Örnek, küçük bir kabul sınamasıdır
- Hata ve uyarıları belgelemek
- Veri ve paket belgeleri
- Üretilmiş paket belgeleri ve geçici Rd laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, knitr, testthat, roxygen2.

Bu komut Bölüm 18–24 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
PACKAGE_ENGINEERING_RUN_ID=okur-bolum-21-01 Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:PACKAGE_ENGINEERING_RUN_ID="okur-bolum-21-01"
Rscript --vanilla scripts/run_package_engineering_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [belgeleme_ve_ornekler.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch21/belgeleme_ve_ornekler.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 20](/r-programlama/bolum-20/) · [Dizin](/r-programlama/) · [Bölüm 22 →](/r-programlama/bolum-22/)
