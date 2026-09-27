---
layout: page
title: "Bölüm 31 · CRAN gönderimi ve geri bildirim"
permalink: /r-programlama/bolum-31/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- CRAN son test sunucusu değildir
- Gönderim nesnesini sabitlemek
- Gönderim günü metadata denetimi
- cran-comments.md: kısa bir kanıt özeti
- Form, e-posta doğrulaması ve gelen alanı
- Tanıdan eylem ve kanıta
- CRAN geri bildirimine yanıt vermek
- Ad çakışması gönderim yorumuyla aşılmaz
- Gizlilik ve iletişim güvenliği

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 30–32 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
RELEASE_READINESS_RUN_ID=okur-bolum-31-01 Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:RELEASE_READINESS_RUN_ID="okur-bolum-31-01"
Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [cran_geri_bildirim.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch31/cran_geri_bildirim.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

Bu test GitHub, CRAN veya sglasso deposunu değiştirmez. sglasso ad denetimi tarihli, çevrimdışı bir öğretim kaydıdır; canlı ad taraması değildir.

[← Bölüm 30](/r-programlama/bolum-30/) · [Dizin](/r-programlama/) · [Bölüm 32 →](/r-programlama/bolum-32/)
