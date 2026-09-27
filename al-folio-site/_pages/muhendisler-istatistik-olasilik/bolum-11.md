---
layout: page
title: "Bölüm 11: Örnekleme, bootstrap ve jackknife"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-11/"
description: "Ortanca gibi doğrusal olmayan bir tahmin edicinin örnekleme belirsizliğini yeniden örneklemeyle incelemek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/11_ornekleme_bootstrap.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/11-ornekleme-bootstrap.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Ortanca gibi doğrusal olmayan bir tahmin edicinin örnekleme belirsizliğini yeniden örneklemeyle incelemek.

## Veri ve birimler

Sentetik ölçüm örneği; değerler ölçüm biriminde, yeniden örnekleme indisleri boyutsuzdur.

## Yöntem

Sabit tohumla bootstrap örnekleri ve bırak-bir-dışarı jackknife tahminleri oluşturulur.

## Varsayım kontrolleri

- Gözlemlerin hedef anakütleyi temsil ettiği tartışılır.
- Bootstrap'ın bağımsız ve özdeş dağılım yaklaşımına dayandığı belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/11_ornekleme_bootstrap.py
BOOK_SMOKE=1 quarto render labs/r/11-ornekleme-bootstrap.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Bootstrap yüzdelik aralığı
- Bootstrap ve jackknife standart hata karşılaştırması

## Yorum ve uygulama görevi

İki standart hata tahmininin ayrışmasının olası nedenlerini açıklayın.

Aynı tohum politikasını koruyarak ortalama için bootstrap aralığı üretin ve ortanca aralığıyla karşılaştırın.

## Varsayımı zorlayın

Teknik tekrarları satır ve parça düzeyinde ayrı ayrı yeniden örnekleyin; iki standart hata arasındaki farkı bağımsız bilgi birimiyle açıklayın.
