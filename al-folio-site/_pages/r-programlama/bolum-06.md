---
layout: page
title: "Bölüm 6 · İfadeler ve akış denetimi"
permalink: /r-programlama/bolum-06/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- İfade bir değer üretir
- İşleçlerin önceliği niyeti gizlememelidir
- Koşul tek bir karar ister
- Koşu sayısı akış denetimini somutlaştırır
- Döngünün sonlanması sözleşmenin parçasıdır
- Durum, geçmişin gerekli özetidir
- Beklenen değer bağımsız bir kontrol sağlar
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 6–10 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
LANGUAGE_CORE_RUN_ID=okur-bolum-06-01 Rscript --vanilla scripts/run_language_core_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:LANGUAGE_CORE_RUN_ID="okur-bolum-06-01"
Rscript --vanilla scripts/run_language_core_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [ifadeler_ve_akis.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch06/ifadeler_ve_akis.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 5](/r-programlama/bolum-05/) · [Dizin](/r-programlama/) · [Bölüm 7 →](/r-programlama/bolum-07/)
