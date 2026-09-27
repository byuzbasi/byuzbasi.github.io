---
layout: page
title: "Bölüm 14: Hipotez testleri, güç ve eşdeğerlik"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-14/"
description: "Tek örneklem testini güven aralığı, güç ve mühendislik önem eşiğiyle birlikte yorumlamak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/14_hipotez_testleri.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/14-hipotez-testleri.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Tek örneklem testini güven aralığı, güç ve mühendislik önem eşiğiyle birlikte yorumlamak.

## Veri ve birimler

Sentetik proses ortalaması, standart sapma ve örneklem büyüklüğü; ölçümler fiziksel birimdedir.

## Yöntem

t istatistiği ve p-değeri hesaplanır; seçilen etki büyüklüğü için güç ve eşdeğerlik mantığı incelenir.

## Varsayım kontrolleri

- Yönlü hipotezin veriyi görmeden önce belirlenmesi gerektiği vurgulanır.
- Bağımsızlık, yaklaşık normallik ve pratik önem eşiği değerlendirilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/14_hipotez_testleri.py
BOOK_SMOKE=1 quarto render labs/r/14-hipotez-testleri.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Test ve güven aralığı özeti
- Etki büyüklüğüne göre güç tablosu

## Yorum ve uygulama görevi

İstatistiksel anlamlılık ile mühendislik öneminin neden aynı olmadığını açıklayın.

Hedeflenen gücü yüzde 90 yapıp aynı etki için gerekli örneklem büyüklüğünü bulun.

## Varsayımı zorlayın

Yanlış alarm ve kaçırma maliyetlerini değiştirin; en küçük p-değeri yerine beklenen kayıp ve zorunlu hata sınırlarıyla test seçin.
