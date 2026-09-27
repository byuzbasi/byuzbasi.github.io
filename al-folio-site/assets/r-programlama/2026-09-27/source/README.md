# R Programlama ve Paket Geliştirme — uygulama kodları

Yazar: Prof. Dr. Bahadır Yüzbaşı. Kod sürümü: 2026-09-27.

https://byuzbasi.github.io/r-programlama/

Arşivi açın; R_programlama dizinini çalışma dizini yapın. Dizin yapısını koruyun.
R 4.6.0 ile sınandı; yalnız bu sürümün desteklendiği anlamına gelmez.
Bölüm sayfaları gerekli paketleri ve POSIX/PowerShell komutlarını açıklar.
Paketleri otomatik kuran bir betik yoktur. Derleyiciler yalnız 25–29 için gerekir.
Küçük testler yeni validation/v0.1/<run-id> dizinine yazar ve aynı kimliği reddeder.
13–17 testi yalnız 64 tekrarlı öğretim örneğidir; üretim araştırması değildir.
30–32 çevrimdışı testleri GitHub veya CRAN'a gönderim yapmaz.
Paket kontrol betiği kopyadaki roxygen belgelerini yeniler, yerel build/install/check yapar;
CRAN gönderimi yapmaz. R CMD check ağ üzerinden CRAN durumunu sorgulayabilir.

## Hızlı başlangıç

```sh
cd /absolute/path/to/R_programlama
Rscript --vanilla companion/v0.1/examples/ch01/ilk_oturum.R
```

## Bütünlük

manifest.json her kaynak dosyasının SHA-256 özetini ve boyutunu içerir.
manifest kendisini kapsamaz. Kitabın PDF'si, özel veriler ve Git geçmişi bu arşivde yoktur.
BernoulliRuns kaynak paketi CRAN'da yayımlanmış olarak sunulmaz.
