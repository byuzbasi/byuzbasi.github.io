---
layout: page
title: "Bölüm 8: Sürekli olasılık dağılımları"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-08/"
description: "Normal şartname olasılığını ve Weibull sağkalımını doğru parametreleştirmeyle hesaplamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/08_surekli_dagilimlar.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/08-surekli-dagilimlar.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Normal şartname olasılığını ve Weibull sağkalımını doğru parametreleştirmeyle hesaplamak.

## Veri ve birimler

Sentetik boyut ölçümleri mm ve ömürler saat; olasılıklar boyutsuzdur.

## Yöntem

Normal dağılımın iki sınır arasındaki alanı ile Weibull sağkalım ve yüzdelikleri hesaplanır.

## Varsayım kontrolleri

- Normal modelde standart sapmanın pozitif olduğu denetlenir.
- Weibull biçim ve ölçek parametrelerinin kullanılan yazılım tanımıyla eşleştiği doğrulanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/08_surekli_dagilimlar.py
BOOK_SMOKE=1 quarto render labs/r/08-surekli-dagilimlar.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Şartname içinde kalma olasılığı
- Weibull sağkalım ve ömür yüzdelikleri

## Yorum ve uygulama görevi

Weibull biçim parametresinin yaşlanma mekanizması hakkında ne söylediğini açıklayın.

Ölçek parametresini yüzde 10 artırıp belirlenen saatteki sağkalım değişimini hesaplayın.

## Varsayımı zorlayın

Aynı medyana sahip üstel ve Weibull modellerinin erken arıza yüzdeliklerini karşılaştırın; sabit tehlike varsayımının karar etkisini açıklayın.
