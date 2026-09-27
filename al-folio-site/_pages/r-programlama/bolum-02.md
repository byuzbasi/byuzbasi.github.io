---
layout: page
title: "Bölüm 2 · Nesneler, değerler ve atomik vektörler"
permalink: /r-programlama/bolum-02/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Ad, kutunun üzerindeki etikettir
- Atomik vektör temel veri taşıyıcısıdır
- Tür, sınıf, uzunluk ve yapı aynı soru değildir
- Adlar bir özelliktir
- Bir atomik vektörün tek türü vardır
- Eksiklik ile yokluk farklıdır
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 2–5 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
FOUNDATIONS_RUN_ID=okur-bolum-02-01 Rscript --vanilla scripts/run_foundations_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:FOUNDATIONS_RUN_ID="okur-bolum-02-01"
Rscript --vanilla scripts/run_foundations_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [nesneler_ve_vektorler.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch02/nesneler_ve_vektorler.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 1](/r-programlama/bolum-01/) · [Dizin](/r-programlama/) · [Bölüm 3 →](/r-programlama/bolum-03/)
