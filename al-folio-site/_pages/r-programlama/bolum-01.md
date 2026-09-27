---
layout: page
title: "Bölüm 1 · R ile çalışmaya başlamak"
permalink: /r-programlama/bolum-01/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Programı açmak, programlamaya başlamak değildir
- R ekosisteminin dört ayrı parçası
- Konsol, betik ve proje
- Kurulumdan ilk çalıştırmaya
- İlk sınanabilir betik
- Bir ifadeyi okumak
- Yardım sistemini kullanmak
- Temiz oturum ve oturum bilgisi

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: Temel R; ek paket gerekmez.

Bu komut yalnız bu bölümün bağımsız örneğini çalıştırır.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
Rscript --vanilla companion/v0.1/examples/ch01/ilk_oturum.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
Rscript --vanilla companion/v0.1/examples/ch01/ilk_oturum.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

4 gözlem, 3 ölçülen gün ve 19.5 C ortalama.

## Bölüm dosyaları

- [ilk_oturum.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch01/ilk_oturum.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

[Dizin](/r-programlama/) · [Bölüm 2 →](/r-programlama/bolum-02/)
