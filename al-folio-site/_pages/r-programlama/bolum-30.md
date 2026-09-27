---
layout: page
title: "Bölüm 30 · Yayıma aday sürüm"
permalink: /r-programlama/bolum-30/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Yayıma aday sürüm bir klasör değil, kanıt durumudur
- Git deposu ile R kaynak paketi aynı nesne değildir
- Sürüm etiketi ve GitHub release
- Sürekli bütünleştirme matrisi
- İş akışı yetkileri, sırlar ve artefaktlar
- Paket sitesi bir kanıtın sunumudur
- BernoulliRuns yayımlama adayının durumu
- Ad denetimi: sglasso vakası
- Çevrimdışı ad ve yayın kapısı örneği
- Yerel yayımlama kapısı

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest.

Bu komut Bölüm 30–32 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
RELEASE_READINESS_RUN_ID=okur-bolum-30-01 Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:RELEASE_READINESS_RUN_ID="okur-bolum-30-01"
Rscript --vanilla scripts/run_release_readiness_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [yayin_adayi_kapisi.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch30/yayin_adayi_kapisi.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

Bu test GitHub, CRAN veya sglasso deposunu değiştirmez. sglasso ad denetimi tarihli, çevrimdışı bir öğretim kaydıdır; canlı ad taraması değildir.

[← Bölüm 29](/r-programlama/bolum-29/) · [Dizin](/r-programlama/) · [Bölüm 31 →](/r-programlama/bolum-31/)
