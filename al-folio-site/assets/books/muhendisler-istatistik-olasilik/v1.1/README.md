# Mühendisler için İstatistik ve Olasılık — uygulamalar v1.1

Yazar: Prof. Dr. Bahadır Yüzbaşı

22 bölüm, 22 Python dosyası ve 22 R/Quarto laboratuvarı. Bu paket öğrenci
uygulamalarını içerir; kitap PDF'si, araştırma sonuçları ve öğretim elemanı çözüm
anahtarı değildir. Bölüm amaçları, varsayımlar, birimler ve görevler
`lab_protocols.json` dosyasındadır.

## Gereksinimler ve güvenli kısa deneme

Python paketlerinin beyan edilen sürümleri `requirements.txt`, testte kullanılan
gerçek sürümler `tested_environment.json` içindedir. R için `knitr` ve `digest`
gerekir. R belgesi oluşturmak için ayrıca Quarto gerekir. Denetimler paket
kurmaz. Eksik bağımlılıkları kendi ortamınızda gözden geçirip kurunuz.

Arşivi açtıktan sonra aşağıdaki mutlak yolu gerçek indirme klasörünüzle değiştirin.
Klasör yapısını koruyun; ortak yardımcılar ve Bölüm 22'nin pilot tablosu gereklidir.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
python3 scripts/check_python_labs.py --smoke
BOOK_SMOKE=1 Rscript --vanilla scripts/check_r_labs.R
```

Kısa denemeler simülasyon/yeniden örnekleme yapılan laboratuvarlarda 64 tekrar
kullanır. Referans Monte Carlo hassasiyetini kanıtlamaz; kod yolu, boyutlar,
sınırlar ve analitik kontrolleri sınar. `BOOK_SMOKE=1` olmadan bazı laboratuvarlar
daha çok tekrar yapar. İlk kullanımda kısa deneme önerilir. Python ve R aynı
tohumla aynı rastgele sayıları üretmek zorunda değildir.

Tek bölüm örneği:

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/01_muhendislikte_belirsizlik.py
BOOK_SMOKE=1 quarto render labs/r/01-muhendislikte-belirsizlik.qmd --to html
```

Python sonuçları terminale, R derlemesi ilgili laboratuvarın HTML dosyasına yazılır.
Otomatik R denetimi grafikleri geçici dosyada tutar; kaynak ve veri değiştirilmez.
Tablo çıktıları `knitr::kable()` kullanır.

## Veri kökeni ve doğrulama

Örnekler kod içine gömülü sentetik öğretim verileridir. `tables/generated/v1/pilot_summary.csv`,
kitabın sentetik çekme dayanımı pilotunun korunmuş özetidir; Bölüm 22 bu dosyanın
yalnız boyutunu ve SHA-256 özetini okur. Ham veri pakete dahil edilmemiştir.
`manifest.json` her dağıtım dosyasının bayt ve SHA-256 bilgisini verir; manifest
kendisini içermez. `python3 scripts/verify_manifest.py` ile dosyaları doğrulayın.

İçerik ve telif: Prof. Dr. Bahadır Yüzbaşı. Yeniden dağıtım ve diğer kullanım
koşulları için yazarla iletişime geçiniz. Bu paket açık kaynak lisansı ilan etmez.

Web: https://byuzbasi.github.io/books/muhendisler-istatistik-olasilik/
