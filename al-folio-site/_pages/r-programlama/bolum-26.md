---
layout: page
title: "Bölüm 26 · Rcpp ile ilk çekirdek"
permalink: /r-programlama/bolum-26/
lang: tr
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · Kod sürümü 2026-09-27

[Tüm bölümler](/r-programlama/) · [Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip)

## Konular

- Köprü, bilimsel sözleşmenin yerine geçmez
- Birinci laboratuvar: öznitelikle dışa açılan işlev
- R ile C++ türlerini eşlemek
- İndis ve uzunluk güvenliği
- Görünüm, kopya ve çıktı sahipliği
- Hata iletimi ve kaynak yaşamı
- Kullanıcı kesmesi
- Derleme ve küçük eşdeğerlik sınaması

## Ön koşullar ve çalıştırma

Gerekli kurulu bileşenler: jsonlite, digest, Rcpp, RcppArmadillo; C/C++ ve Fortran derleyicileri.

Bu komut Bölüm 25–29 ortak test grubunu çalıştırır; tek dosyanın bağımsız çalıştığı iddiası değildir. Yardımcı işlevler ve girdiler birlikte yüklenir.

Önce tam arşivi açın. Aşağıdaki yolu arşivden çıkan `R_programlama` dizininin gerçek tam yoluyla değiştirin. `Rscript` PATH üzerinde bulunmalıdır.

macOS/Linux (Terminal):

```sh
cd /absolute/path/to/R_programlama
NATIVE_RUN_ID=okur-bolum-26-01 Rscript --vanilla scripts/run_native_smoke.R
```

Windows (PowerShell):

```powershell
cd "C:/path/to/R_programlama"
$env:NATIVE_RUN_ID="okur-bolum-26-01"
Rscript --vanilla scripts/run_native_smoke.R
```

Test grubunu yeniden çalıştırırken `01` son ekini `02` yapın; önceki sonuçlar korunur. Grup sonuçları `validation/v0.1/<run-id>/` altında, sürüm ve bütünlük kayıtlarıyla saklanır.

## Beklenen sonuç

Komut sıfır çıkış koduyla tamamlanır; test raporunda tüm kapılar PASS/TRUE olmalıdır. Eksik paket/derleyici durumunda başarı varsayılmaz; hata iletisini izleyin.

## Bölüm dosyaları

- [rcpp_ilk_cekirdek.R](/assets/r-programlama/2026-09-27/source/companion/v0.1/examples/ch26/rcpp_ilk_cekirdek.R)

Tek dosya bağlantıları inceleme içindir. Çalıştırmak için tam arşiv önerilir; ortak saf-R referansı ve diğer bölüm dosyaları gerekebilir.

Yerel kod bu sürümde R, Rcpp, C API ve Fortran sonuçlarını küçük girdilerde karşılaştırır; hız üstünlüğü veya BernoulliRuns'ın yerel çekirdek içerdiği iddia edilmez.

[← Bölüm 25](/r-programlama/bolum-25/) · [Dizin](/r-programlama/) · [Bölüm 27 →](/r-programlama/bolum-27/)
