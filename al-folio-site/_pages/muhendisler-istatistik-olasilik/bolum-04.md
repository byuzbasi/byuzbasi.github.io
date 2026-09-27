---
layout: page
title: "Bölüm 4: Sayma ve olasılığın temelleri"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-04/"
description: "Olay cebrini, dahil etme-dışlama ilkesini ve küçük bir örnek uzayın tam sayımını doğrulamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/04_olasilik_temelleri.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/04-olasilik-temelleri.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Olay cebrini, dahil etme-dışlama ilkesini ve küçük bir örnek uzayın tam sayımını doğrulamak.

## Veri ve birimler

Üç ikili sensörün sekiz olası durumu; durum göstergeleri ve olasılıklar boyutsuzdur.

## Yöntem

Örnek uzay tam olarak üretilir; birleşim, kesişim ve tümleyen olayları sayım yoluyla hesaplanır.

## Varsayım kontrolleri

- Örnek uzayın bütün durumları yalnız bir kez içerdiği doğrulanır.
- Eş olasılık kabulünün yalnız öğretim modeline ait olduğu belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/04_olasilik_temelleri.py
BOOK_SMOKE=1 quarto render labs/r/04-olasilik-temelleri.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Sekiz durumluk olay tablosu
- Dahil etme-dışlama eşitliği denetimi

## Yorum ve uygulama görevi

Sensörlerin eş olasılıklı olmadığı durumda tam sayımın nasıl ağırlıklandırılacağını açıklayın.

Dört sensörlü sisteme genişletip en az üç alarm olayının olasılığını hesaplayın.

## Varsayımı zorlayın

Sensör durumlarının eş olasılıklı olmadığını kabul edin; durumları fiziksel olasılıklarla ağırlıklandırıp bağımsızlık gereksinimini belirtin.
