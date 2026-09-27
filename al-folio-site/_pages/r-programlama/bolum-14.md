---
layout: page
title: "Bölüm 14 · Grafiklerle iletişim"
permalink: /r-programlama/bolum-14/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Önce soru, sonra işaret
- Base R grafiği: aygıt ve ardışık çizim
- Katmanlı grafik yaklaşımı
- Ölçek, koordinat ve eksen dürüstlüğü
- Erişilebilirlik ve baskı
- Dışa aktarma ve sürümleme
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, dplyr, tidyr, ggplot2, knitr, renv.

Bu komut Bölüm 13–17 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
REPRO_RESEARCH_RUN_ID=okur-bolum-14-01 Rscript --vanilla scripts/run_reproducible_research_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:REPRO_RESEARCH_RUN_ID="okur-bolum-14-01"
Rscript --vanilla scripts/run_reproducible_research_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [grafiklerle_iletisim.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch14/grafiklerle_iletisim.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 13](/r-programlama/bolum-13/) · [Dizin](/r-programlama/) · [Bölüm 15 →](/r-programlama/bolum-15/)
