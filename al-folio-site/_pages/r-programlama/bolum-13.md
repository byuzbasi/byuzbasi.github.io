---
layout: page
title: "Bölüm 13 · Veriyi dönüştürmek"
permalink: /r-programlama/bolum-13/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Dönüşümden önce veri sözleşmesi
- Uzun tabloyu tek kaynaktan üretmek
- Seçmek, türetmek ve gruplamak
- Birleştirme: anahtar ve kardinalite
- Uzun ve geniş biçim arasında gidip gelmek
- Base R mi tidyverse mü?
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, dplyr, tidyr, ggplot2, knitr, renv.

Bu komut Bölüm 13–17 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
REPRO_RESEARCH_RUN_ID=okur-bolum-13-01 Rscript --vanilla scripts/run_reproducible_research_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:REPRO_RESEARCH_RUN_ID="okur-bolum-13-01"
Rscript --vanilla scripts/run_reproducible_research_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [veriyi_donusturmek.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch13/veriyi_donusturmek.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 12](/r-programlama/bolum-12/) · [Dizin](/r-programlama/) · [Bölüm 14 →](/r-programlama/bolum-14/)
