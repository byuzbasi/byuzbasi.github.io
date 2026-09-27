---
layout: page
title: "Bölüm 1: Mühendislikte belirsizlik ve karar"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-01/"
description: "Olasılık ile sonuç büyüklüğünü ayırmak, beklenen kaybı hesaplamak ve kararın maliyet varsayımlarına duyarlılığını görmek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/01_muhendislikte_belirsizlik.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/01-muhendislikte-belirsizlik.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Olasılık ile sonuç büyüklüğünü ayırmak, beklenen kaybı hesaplamak ve kararın maliyet varsayımlarına duyarlılığını görmek.

## Veri ve birimler

Sentetik iki eylem ve iki durum tablosu; olasılıklar boyutsuz, kayıplar para birimi cinsindedir.

## Yöntem

Her eylem için olasılık ağırlıklı kayıp hesaplanır ve duyarlılık ızgarasında en küçük beklenen kayıplı eylem seçilir.

## Varsayım kontrolleri

- Durum olasılıkları 1'e toplamlanır.
- Kayıplar aynı para biriminde ve aynı karar ufkunda tanımlanır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/01_muhendislikte_belirsizlik.py
BOOK_SMOKE=1 quarto render labs/r/01-muhendislikte-belirsizlik.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Eylem bazında beklenen kayıp tablosu
- Eşik olasılığı ve duyarlılık özeti

## Yorum ve uygulama görevi

En düşük beklenen kayıplı kararın hangi maliyet veya olasılık aralığında değiştiğini açıklayın.

Yanlış alarm maliyetini yüzde 25 artırıp karar eşiğini yeniden hesaplayın ve mühendislik sonucunu yazın.

## Varsayımı zorlayın

Arıza kaybını iki katına çıkarın; kararın hangi başabaş aralığında değiştiğini ve güvenlik kısıtının neden ayrı kaldığını açıklayın.
