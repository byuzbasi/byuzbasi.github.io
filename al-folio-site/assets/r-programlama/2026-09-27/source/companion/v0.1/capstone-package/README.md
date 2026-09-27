# BernoulliRuns yaşayan paket çalışma alanı

Yaşayan paketin bilimsel yönü onaylanmıştır: dışarıdan verilen, konuma özgü
başarı olasılıkları altında bağımsız Bernoulli dizisinin koşu sayısı için kesin
dağılım hesaplanır. Tam sözleşme
`editorial/v0.1/yasayan_paket_sozlesmesi.md` dosyasındadır.

`BernoulliRuns/`, GPL (>= 3) lisanslı gerçek yerel paket adayıdır. İlk sürümün
kamusal API'si `count_runs()`, `runs_distribution()`, `runs_mean()` ve
`runs_tail()` işlevlerinden oluşur. `prototype/bernoulli_runs_reference.R`,
paketten ayrı tutulan ve kitap boyunca değişmeden korunacak saf-R bilimsel
referanstır.

Yerel paket adayını doğrulamak için proje kökünden yeni bir çalışma kimliğiyle
şu komut kullanılır:

```sh
BERNOULLI_RUNS_CHECK_ID=v0.1-bernoulli-runs-package-04 Rscript --vanilla scripts/run_bernoulli_runs_package_check.R
```

Doğrulama; roxygen2 üretimini, testleri, `n = 1,...,8` tam sayımını, prototip
eşdeğerliğini, kaynak arşivi oluşturmayı, yalıtılmış kurulumu, temiz oturumu ve
`R CMD check --as-cran` denetimini kapsar. Mevcut doğrulama kayıtlarının üzerine
yazılmaz.

Gelecekteki Rcpp ve modern Fortran çekirdekleri ancak ayrı onay ve eşdeğerlik
protokolü sonrasında bu referansla aynı giriş, çıktı ve hata sözleşmesine
uyacaktır. AXPY örneği yalnızca
`companion/v0.1/examples/ch29/` altında bulunan yerel arayüz duman
sınamasıdır ve CRAN'a aday yaşayan paket değildir.
