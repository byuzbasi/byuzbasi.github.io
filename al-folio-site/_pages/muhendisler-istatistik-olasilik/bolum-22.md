---
layout: page
title: "Bölüm 22: Bütünleşik mühendislik vakaları"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-22/"
description: "Asimetrik karar kaybını yeniden üretilebilir çıktı manifestiyle birleştirerek uçtan uca vaka raporu kurmak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/22_butunlesik_vakalar.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/22-butunlesik-vakalar.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Asimetrik karar kaybını yeniden üretilebilir çıktı manifestiyle birleştirerek uçtan uca vaka raporu kurmak.

## Veri ve birimler

Sentetik karar olasılıkları ve kayıpları ile salt-okunur pilot çıktı; kayıplar para birimi, dosya boyutu bayttır.

## Yöntem

Eylemler beklenen kayıpla karşılaştırılır; mevcut çıktı için boyut ve SHA-256 özeti kaydedilir.

## Varsayım kontrolleri

- Kaynak dosyanın değiştirilmediği ve yalnız okunarak özetlendiği doğrulanır.
- Karar olasılıkları, maliyet ufku ve model sınırları raporlanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/22_butunlesik_vakalar.py
BOOK_SMOKE=1 quarto render labs/r/22-butunlesik-vakalar.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Karar kaybı ve seçilen eylem
- Dosya boyutu ve SHA-256 içeren manifest satırı

## Yorum ve uygulama görevi

İstatistiksel tahmin, karar eşiği ve yeniden üretilebilirlik kanıtının vaka raporunda nasıl bağlandığını açıklayın.

Alternatif bir yanlış-negatif maliyeti için kararı yeniden hesaplayın ve yeni sonucu ayrı, sürümlü bir manifest kaydıyla belgeleyin.

## Varsayımı zorlayın

Temel, yüksek ve düşük talep senaryolarında kapasite kayıplarını değiştirin; beklenen kayıp ile minimaks kararının dayanıklılık zarfını karşılaştırın.
