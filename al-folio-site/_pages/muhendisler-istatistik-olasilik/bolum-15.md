---
layout: page
title: "Bölüm 15: İki ve çoklu grup karşılaştırmaları"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-15/"
description: "Bağımsız, eşleştirilmiş ve ikili sonuç tasarımlarında uygun karşılaştırma hedefini seçmek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/15_karsilastirmalar.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/15-karsilastirmalar.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Bağımsız, eşleştirilmiş ve ikili sonuç tasarımlarında uygun karşılaştırma hedefini seçmek.

## Veri ve birimler

Sentetik iki kaplama yöntemi ölçümleri ve ikili başarı sayıları; sürekli sonuçlar mikrometredir.

## Yöntem

Eşit varyans zorlamadan Welch karşılaştırması; eşleştirilmiş fark ve oran farkı hesapları yapılır.

## Varsayım kontrolleri

- Bağımsız ve eşleştirilmiş tasarımların karıştırılmadığı doğrulanır.
- Gruplarda aynı sonuç tanımı ve karşılaştırılabilir ölçüm süreci kullanılır.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/15_karsilastirmalar.py
BOOK_SMOKE=1 quarto render labs/r/15-karsilastirmalar.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Welch fark tahmini ve aralığı
- Eşleştirilmiş ve ikili sonuç özetleri

## Yorum ve uygulama görevi

Tasarım bilgisinin standart hata ve karar üzerindeki etkisini açıklayın.

Eşleştirilmiş veriyi bağımsızmış gibi analiz edip standart hata farkını nicelleştirin.

## Varsayımı zorlayın

Eş kimliklerini kaldırıp veriyi bağımsız analiz edin; standart hata kaybını hesaplayın ve hangi tahmin hedefiın korunup hangisinin değiştiğini açıklayın.
