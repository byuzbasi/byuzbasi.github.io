---
layout: page
title: "Bölüm 12: Nokta tahmini ve olabilirlik"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-12/"
description: "Üstel ömür modelinin maksimum olabilirlik tahminini analitik ve sayısal yollarla doğrulamak ve aykırılığa duyarlılığı görmek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/12_nokta_tahmini.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/12-nokta-tahmini.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Üstel ömür modelinin maksimum olabilirlik tahminini analitik ve sayısal yollarla doğrulamak ve aykırılığa duyarlılığı görmek.

## Veri ve birimler

Sentetik sansürsüz ömürler saat cinsindedir; hız parametresi saat üzeri eksi bir birimindedir.

## Yöntem

Log-olabilirlik ençoklanır; analitik hız tahmini ve kırpılmış ortalama duyarlılığı karşılaştırılır.

## Varsayım kontrolleri

- Ömürlerin pozitif ve sansürsüz olduğu denetlenir.
- Sabit tehlike ve bağımsız gözlem varsayımları değerlendirilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/12_nokta_tahmini.py
BOOK_SMOKE=1 quarto render labs/r/12-nokta-tahmini.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Analitik ve sayısal maksimum olabilirlik tahminleri
- Sağlamlık duyarlılık özeti

## Yorum ve uygulama görevi

Üstel modelin büyük ömür gözlemlerine duyarlılığını ve fiziksel anlamını açıklayın.

En büyük ömrü iki katına çıkarıp hız ve ortalama ömür tahminlerindeki değişimi raporlayın.

## Varsayımı zorlayın

En büyük ömür gözlemini iki katına çıkarın; hız tahmini değişimini üstel sabit tehlike ve karışım olasılığı açısından yorumlayın.
