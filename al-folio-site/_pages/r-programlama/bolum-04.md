---
layout: page
title: "Bölüm 4 · Bileşik veri yapıları"
permalink: /r-programlama/bolum-04/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Veri yapısı bir sözleşmedir
- Liste farklı türde bileşenleri birlikte taşır
- Matris, boyut özelliği olan atomik vektördür
- Dizi ikiden çok boyutu taşır
- Faktör kategori sözleşmesini taşır
- Veri çerçevesi eşit uzunluklu sütunlar listesidir
- Basitleştirme boyutu sessizce kaldırabilir
- Yapılar arasında dönüşüm kayıpsız olmayabilir
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 2–5 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
FOUNDATIONS_RUN_ID=okur-bolum-04-01 Rscript --vanilla scripts/run_foundations_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:FOUNDATIONS_RUN_ID="okur-bolum-04-01"
Rscript --vanilla scripts/run_foundations_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [bilesik_veri_yapilari.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch04/bilesik_veri_yapilari.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 3](/r-programlama/bolum-03/) · [Dizin](/r-programlama/) · [Bölüm 5 →](/r-programlama/bolum-05/)
