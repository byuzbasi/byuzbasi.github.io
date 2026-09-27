---
layout: page
title: "Bölüm 5: Koşullu olasılık, Bayes ve güvenilirlik"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-05/"
description: "Bir test sonucuyla önsel arıza olasılığını güncellemek ve seri-paralel sistem güvenilirliğini karşılaştırmak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/05_kosullu_olasilik_bayes.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/05-kosullu-olasilik-bayes.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Bir test sonucuyla önsel arıza olasılığını güncellemek ve seri-paralel sistem güvenilirliğini karşılaştırmak.

## Veri ve birimler

Sentetik prevalans, duyarlılık, seçicilik ve bileşen güvenilirlikleri; tümü boyutsuz oranlardır.

## Yöntem

Bayes teoremiyle sonsal olasılık; bağımsız bileşen varsayımıyla seri ve paralel güvenilirlik hesaplanır.

## Varsayım kontrolleri

- Koşullu olasılıkların 0 ile 1 arasında olduğu doğrulanır.
- Bileşen bağımsızlığının ortak nedenli arızalarda geçersiz olabileceği belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/05_kosullu_olasilik_bayes.py
BOOK_SMOKE=1 quarto render labs/r/05-kosullu-olasilik-bayes.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Bayes güncelleme tablosu
- Sistem düzenlerine göre güvenilirlik tablosu

## Yorum ve uygulama görevi

Pozitif testin neden tek başına arıza kanıtı olmadığını ve taban oranın rolünü açıklayın.

Önsel arıza olasılığını yarıya indirip pozitif öngörü değerini yeniden hesaplayın.

## Varsayımı zorlayın

İki testin aynı sinyali kullandığı koşullu bağımlılık senaryosu kurun; bağımsızlık hesabının sonsal olasılığı ne yönde bozduğunu gösterin.
