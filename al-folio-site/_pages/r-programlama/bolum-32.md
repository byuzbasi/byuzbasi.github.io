---
layout: page
title: "Bölüm 32 · Bakımı yapılabilir bir paket"
permalink: /r-programlama/bolum-32/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Yayın bitiş değil, yeni bir sözleşmenin başlangıcıdır
- Sürüm numarası bir değişiklik özeti değildir
- Kamusal API yüzeyini envanterlemek
- Kullanımdan kaldırma bir geçiş dönemidir
- Ters bağımlılıklar
- Bilimsel ve sayısal geriye uyumluluk
- Veri, serileştirme ve belge bakımı
- Yerel kodun uzun dönem bakımı
- Güvenlik ve bakımcı kimliği
- Arşivlenme, yetim kalma ve devir
- sglasso için bakım dersi
- Bakım kapısını birleştirmek
- Kitabın bütünleşik bitirme projesi
- Düzeye göre devam yolları

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 30–32 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
RELEASE_READINESS_RUN_ID=okur-bolum-32-01 Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:RELEASE_READINESS_RUN_ID="okur-bolum-32-01"
Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [bakim_matrisi.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch32/bakim_matrisi.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

Bu test GitHub, CRAN veya sglasso deposunu değiştirmez. sglasso ad denetimi tarihli, çevrimdışı bir öğretim kaydıdır; canlı ad taraması değildir.

[← Bölüm 31](/r-programlama/bolum-31/) · [Dizin](/r-programlama/)
