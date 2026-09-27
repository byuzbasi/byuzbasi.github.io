---
layout: page
title: "Bölüm 19 · Bir paketin tamamını ilk kez görmek"
permalink: /r-programlama/bolum-19/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Paket bir klasörden fazlasıdır
- En küçük anlamlı kaynak ağacı
- Bütün oyun: kısa ama tam çevrim
- Kolaylaştırıcı araç ile temel mekanizma
- Bilimsel sözleşme ile paket altyapısını ayırmak
- Bir CRAN notunu okumak
- Paket ağacını değiştirmeden incelemek

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: Temel R; ek paket gerekmez.

Bu komut yalnız bu bölümün bağımsız örneğini çalıştırır.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
Rscript --vanilla companion/v0.1/examples/ch19/paket_agacini_incelemek.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
Rscript --vanilla companion/v0.1/examples/ch19/paket_agacini_incelemek.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Paket ağacı altı bileşen için TRUE ve PASS verir; dosya değiştirmez.

## Bölüm dosyaları

- [paket_agacini_incelemek.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch19/paket_agacini_incelemek.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[← Bölüm 18](/r-programlama/bolum-18/) · [Dizin](/r-programlama/) · [Bölüm 20 →](/r-programlama/bolum-20/)
