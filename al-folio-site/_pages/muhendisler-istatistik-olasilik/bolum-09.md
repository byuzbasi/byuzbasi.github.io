---
layout: page
title: "Bölüm 9: Ortak dağılımlar ve hata yayılımı"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-09/"
description: "Kovaryansın iki sensör ortalamasının belirsizliğine katkısını nicelleştirmek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/09_ortak_dagilimlar.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/09-ortak-dagilimlar.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Kovaryansın iki sensör ortalamasının belirsizliğine katkısını nicelleştirmek.

## Veri ve birimler

Sentetik iki sensör ölçümü; sensör çıktıları aynı fiziksel birimde, korelasyon boyutsuzdur.

## Yöntem

Kovaryans matrisi kullanılarak doğrusal birleşimin varyansı farklı korelasyon senaryolarında hesaplanır.

## Varsayım kontrolleri

- Kovaryans matrisinin simetrik ve pozitif yarı tanımlı olduğu denetlenir.
- Sensörlerin aynı büyüklüğü ve uyumlu birimlerle ölçtüğü doğrulanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/09_ortak_dagilimlar.py
BOOK_SMOKE=1 quarto render labs/r/09-ortak-dagilimlar.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Korelasyon senaryolarına göre standart hata
- Kovaryans katkılarının tablosu

## Yorum ve uygulama görevi

Pozitif korelasyonun sensör ortalamasından beklenen kazancı neden azalttığını açıklayın.

Farklı hassasiyette iki sensör için en küçük varyanslı doğrusal ağırlıkları hesaplayın.

## Varsayımı zorlayın

Korelasyonu sıfır, pozitif ve negatif yapın; kovaryans matrisinin geçerliliğini ve optimum sensör ağırlıklarını her durumda denetleyin.
