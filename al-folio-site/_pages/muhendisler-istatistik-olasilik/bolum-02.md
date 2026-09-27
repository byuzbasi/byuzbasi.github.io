---
layout: page
title: "Bölüm 2: Veri, ölçme ve deney"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-02/"
description: "Kalibrasyon sapmasını, tekrarlanabilirliği ve örnekleme biçiminin tahmin üzerindeki etkisini ayırmak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/02_veri_olcme_deney.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/02-veri-olcme-deney.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Kalibrasyon sapmasını, tekrarlanabilirliği ve örnekleme biçiminin tahmin üzerindeki etkisini ayırmak.

## Veri ve birimler

Sentetik referans ve cihaz ölçümleri; ölçümler aynı fiziksel birimde, örnekleme göstergeleri boyutsuzdur.

## Yöntem

Sapma ve örneklem standart sapması hesaplanır; rastgele ve kolayda örneklerin ortalamaları karşılaştırılır.

## Varsayım kontrolleri

- Referans değerlerin izlenebilir olduğu kabul edilir.
- Satırlar silinmeden eksik ve sonlu değer denetimi yapılır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/02_veri_olcme_deney.py
BOOK_SMOKE=1 quarto render labs/r/02-veri-olcme-deney.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Kalibrasyon özeti
- Örnekleme tasarımlarına göre ortalama karşılaştırması

## Yorum ve uygulama görevi

Ölçüm hatası ile seçim yanlılığının neden aynı düzeltmeyle giderilemeyeceğini açıklayın.

Örneklem büyüklüğünü iki katına çıkarıp rastgele örnekleme değişkenliğini ve kolayda örnekleme yanlılığını karşılaştırın.

## Varsayımı zorlayın

Kalibrasyon doğrusuna çalışma aralığının dışında bir ölçüm ekleyin; dışdeğerleme ile seçim yanlılığını ayrı ayrı tartışın.
