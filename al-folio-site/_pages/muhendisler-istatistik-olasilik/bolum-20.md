---
layout: page
title: "Bölüm 20: Güvenilirlik, sağkalım ve risk"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-20/"
description: "Sistem topolojisi ile sansürlü ömür bilgisinin güvenilirlik hesabındaki farklı rollerini göstermek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/20_guvenilirlik_risk.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/20-guvenilirlik-risk.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Sistem topolojisi ile sansürlü ömür bilgisinin güvenilirlik hesabındaki farklı rollerini göstermek.

## Veri ve birimler

Sentetik bileşen güvenilirlikleri boyutsuz; olay veya sansür zamanları saattir.

## Yöntem

Seri-paralel sistem olasılıkları ve risk kümeleri üzerinden Kaplan-Meier sağkalımı hesaplanır.

## Varsayım kontrolleri

- Bileşen bağımsızlığı ve ortak nedenli arıza olasılığı tartışılır.
- Sansürün olay mekanizmasından bağımsız olduğu varsayımı değerlendirilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/20_guvenilirlik_risk.py
BOOK_SMOKE=1 quarto render labs/r/20-guvenilirlik-risk.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Sistem güvenilirliği özeti
- Kaplan-Meier risk kümesi ve sağkalım tablosu

## Yorum ve uygulama görevi

Sansürlü bir gözlemin neden olay olarak sayılmadığını fakat sonraki risk kümesini değiştirdiğini açıklayın.

Bir ortak nedenli arıza olasılığı ekleyip ideal bağımsızlık sonucuyla duyarlılık karşılaştırması yapın.

## Varsayımı zorlayın

Paralel bileşenlere ortak güç arızası ekleyin; ideal bağımsız güvenilirlik ile görev profilli sonucu ayrı raporlayın.
