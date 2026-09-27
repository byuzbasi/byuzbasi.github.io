---
layout: page
title: "Bölüm 8 · Ortamlar ve kapsam"
permalink: /r-programlama/bolum-08/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Ortam, değerlerin adsız kabı değildir
- Her ortamın bir üst bağı vardır
- Sözcüksel kapsam adı tanım yerine göre arar
- Kapanış, veri ile davranışı birlikte taşır
- Yerel olmayan atama dar tutulmalıdır
- Arama yolu ile ad alanı aynı kavram değildir
- Önbellek anahtarı bilimsel girdilerin tamamını temsil etmelidir
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 6–10 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
LANGUAGE_CORE_RUN_ID=okur-bolum-08-01 Rscript --vanilla scripts/run_language_core_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:LANGUAGE_CORE_RUN_ID="okur-bolum-08-01"
Rscript --vanilla scripts/run_language_core_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [ortamlar_ve_kapsam.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch08/ortamlar_ve_kapsam.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 7](/r-programlama/bolum-07/) · [Dizin](/r-programlama/) · [Bölüm 9 →](/r-programlama/bolum-09/)
