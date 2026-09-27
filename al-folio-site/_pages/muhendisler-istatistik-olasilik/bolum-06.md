---
layout: page
title: "Bölüm 6: Rastgele değişkenler ve momentler"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-06/"
description: "Kesikli bir rastgele değişkenin kütle işlevini, momentlerini ve yüzdeliklerini doğrudan hesaplamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/06_rastgele_degiskenler.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/06-rastgele-degiskenler.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Kesikli bir rastgele değişkenin kütle işlevini, momentlerini ve yüzdeliklerini doğrudan hesaplamak.

## Veri ve birimler

Sentetik ek yük düzeyleri kN, bunlara ait olasılık kütleleri boyutsuzdur.

## Yöntem

Kütleler normalleştirilir; beklenen değer, varyans ve dağılım işlevinden yüzdelik bulunur.

## Varsayım kontrolleri

- Olasılıkların negatif olmadığı ve 1'e toplandığı denetlenir.
- Varyans hesabında yük biriminin karesinin kullanıldığı doğrulanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/06_rastgele_degiskenler.py
BOOK_SMOKE=1 quarto render labs/r/06-rastgele-degiskenler.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Kütle ve birikimli olasılık tablosu
- Ortalama, varyans ve yüzdelik özeti

## Yorum ve uygulama görevi

Tasarım yükü seçiminde ortalama ile yüksek yüzdeliğin farklı rollerini açıklayın.

En yüksek yükün olasılığını iki katına çıkarıp kütleleri yeniden normalleştirin ve yüzde 95'lik değeri bulun.

## Varsayımı zorlayın

En yüksek yük olasılığını artırıp ortalama, yüzde 95 değer ve kuyruk ortalamasını karşılaştırın; hangi tasarım hedefinin değiştiğini yazın.
