---
layout: page
title: "Bölüm 3: Betimsel istatistik ve veri kalitesi"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-03/"
description: "Merkez, yayılım ve dayanıklı özetleri veri kalite denetimleriyle birlikte hesaplamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/03_betimsel_istatistik.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/03-betimsel-istatistik.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Merkez, yayılım ve dayanıklı özetleri veri kalite denetimleriyle birlikte hesaplamak.

## Veri ve birimler

Sentetik çekme dayanımı ölçümleri; dayanım birimi MPa'dır.

## Yöntem

Ortalama, ortanca, örneklem standart sapması, çeyrekler ve çeyrekler arası açıklık hesaplanır.

## Varsayım kontrolleri

- Tüm değerlerin sonlu ve sayısal olduğu doğrulanır.
- Ortalama ve ortancanın farkı olası çarpıklık veya aykırılık için incelenir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/03_betimsel_istatistik.py
BOOK_SMOKE=1 quarto render labs/r/03-betimsel-istatistik.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Betimsel özet sözlüğü
- Merkez ve yayılım karşılaştırması

## Yorum ve uygulama görevi

Üretim kararında ortalama yerine ortancanın tercih edilebileceği koşulları belirtin.

En büyük gözlemi yüzde 10 artırıp ortalama, ortanca ve standart sapmadaki değişimi raporlayın.

## Varsayımı zorlayın

Bir aykırı değeri silmeden önce ve sonra özetleri yan yana verin; iki sonucun hangi veri üretim açıklaması altında savunulabileceğini yazın.
