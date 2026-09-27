---
layout: page
title: "Bölüm 17: Doğrusal regresyon ve tanılar"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-17/"
description: "Regresyon katsayılarını fiziksel birimleriyle yorumlamak, aralıkları ayırmak ve etkili gözlemleri tanılamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/17_regresyon.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/17-regresyon.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Regresyon katsayılarını fiziksel birimleriyle yorumlamak, aralıkları ayırmak ve etkili gözlemleri tanılamak.

## Veri ve birimler

Sentetik çevrim sayısı ve kapasite kaybı; açıklayıcı değişken çevrim, yanıt yüzde puandır.

## Yöntem

En küçük kareler modeli kurulur; güven/öngörü aralıkları, artıklar ve etki ölçüleri hesaplanır.

## Varsayım kontrolleri

- Doğrusallık, sabit varyans ve artık yapısı incelenir.
- Modelin yalnız gözlenen açıklayıcı değişken aralığında yorumlandığı doğrulanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/17_regresyon.py
BOOK_SMOKE=1 quarto render labs/r/17-regresyon.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Katsayı ve uyum özeti
- Artık ve etkili gözlem tanıları

## Yorum ve uygulama görevi

Eğim katsayısını birimiyle ve nedensellik iddiası kurmadan açıklayın.

En etkili gözlemi yalnız duyarlılık amacıyla dışarıda bırakarak eğim değişimini raporlayın; ana veri setini değiştirmeyin.

## Varsayımı zorlayın

Yeni sensör partisinde artık ortalamasına sabit kayma ekleyin; yalnız kesme düzeltmesi ile eğim değişimi olasılığını tanılarla ayırın.
