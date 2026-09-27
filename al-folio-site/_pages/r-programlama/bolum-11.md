---
layout: page
title: "Bölüm 11 · Yineleme ve işlevsel programlama"
permalink: /r-programlama/bolum-11/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Yineleme, değişen ile sabit kalanı ayırır
- Açık döngü sonuç kabını önceden kurar
- lapply() liste biçimini korur
- vapply() sonuç örneğini sözleşmeye ekler
- Birden çok girdi eşlemeden önce doğrulanır
- Reduce() öğeleri tek bir sonuca katlar
- Yan etkiler ve hatalar yineleme sözleşmesinin parçasıdır
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, R6, rlang.

Bu komut Bölüm 11–12 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
ADVANCED_LANGUAGE_RUN_ID=okur-bolum-11-01 Rscript --vanilla scripts/run_advanced_language_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:ADVANCED_LANGUAGE_RUN_ID="okur-bolum-11-01"
Rscript --vanilla scripts/run_advanced_language_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [yineleme_ve_islevseller.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch11/yineleme_ve_islevseller.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 10](/r-programlama/bolum-10/) · [Dizin](/r-programlama/) · [Bölüm 12 →](/r-programlama/bolum-12/)
