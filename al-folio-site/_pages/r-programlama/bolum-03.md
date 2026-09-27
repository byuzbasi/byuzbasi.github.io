---
layout: page
title: "Bölüm 3 · İndeksleme ve vektörleştirme"
permalink: /r-programlama/bolum-03/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- İndeks, hangi öğenin seçileceğini söyler
- Konumsal seçim
- Negatif indeks dışarıda bırakır
- Mantıksal indeks bir koşulun sonucudur
- Adlı seçim sıraya bağımlılığı azaltır
- Köşeli ayraç sonucun biçimini belirler
- Vektörleştirme işlemin sözleşmesidir
- Geri dönüşüm boyut eşitliği değildir
- Özel sayısal değerleri doğru yüklemle sınamak
- Alt küme ataması veriyi değiştirir
- Bölüm laboratuvarı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 2–5 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
FOUNDATIONS_RUN_ID=okur-bolum-03-01 Rscript --vanilla scripts/run_foundations_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:FOUNDATIONS_RUN_ID="okur-bolum-03-01"
Rscript --vanilla scripts/run_foundations_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [indeksleme_ve_vektorlestirme.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch03/indeksleme_ve_vektorlestirme.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 2](/r-programlama/bolum-02/) · [Dizin](/r-programlama/) · [Bölüm 4 →](/r-programlama/bolum-04/)
