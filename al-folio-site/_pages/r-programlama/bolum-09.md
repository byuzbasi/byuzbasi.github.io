---
layout: page
title: "Bölüm 9 · Tembel değerlendirme"
permalink: /r-programlama/bolum-09/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Argüman önce bir söz olarak bağlanır
- Kullanılmayan ifade çalışmayabilir
- Varsayılan ve sağlanan ifade farklı yerde değerlendirilir
- Eksik argüman ile açıkça verilen değer ayrıdır
- force() değeri belirli anda sabitler
- Döngüde kapanış üretirken bağ paylaşımına dikkat edilir
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 6–10 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
LANGUAGE_CORE_RUN_ID=okur-bolum-09-01 Rscript --vanilla scripts/run_language_core_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:LANGUAGE_CORE_RUN_ID="okur-bolum-09-01"
Rscript --vanilla scripts/run_language_core_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [tembel_degerlendirme.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch09/tembel_degerlendirme.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 8](/r-programlama/bolum-08/) · [Dizin](/r-programlama/) · [Bölüm 10 →](/r-programlama/bolum-10/)
