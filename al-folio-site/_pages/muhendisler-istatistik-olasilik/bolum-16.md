---
layout: page
title: "Bölüm 16: Ki-kare ve parametrik olmayan yöntemler"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-16/"
description: "Kategorik hücre katkılarını ve permütasyon temelli karşılaştırmayı yalnız toplam test sonucunun ötesinde incelemek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/16_ki_kare_parametrik_olmayan.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/16-ki-kare-parametrik-olmayan.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Kategorik hücre katkılarını ve permütasyon temelli karşılaştırmayı yalnız toplam test sonucunun ötesinde incelemek.

## Veri ve birimler

Sentetik arıza kipi sayımları adet ve iki grup ölçümleri fiziksel birimdedir.

## Yöntem

Beklenen hücre sayıları ve ki-kare katkıları hesaplanır; grup etiketleri sabit tohumla permüte edilir.

## Varsayım kontrolleri

- Beklenen hücre sayılarının yaklaşım için yeterliliği denetlenir.
- Permütasyon için değiştirilebilirlik varsayımı değerlendirilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/16_ki_kare_parametrik_olmayan.py
BOOK_SMOKE=1 quarto render labs/r/16-ki-kare-parametrik-olmayan.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Hücre bazında ki-kare katkı tablosu
- Permütasyon p-değeri

## Yorum ve uygulama görevi

Toplam ki-kare sinyalini en çok hangi hücrelerin oluşturduğunu açıklayın.

En seyrek iki kategoriyi birleştirmenin test sonucunu ve yorumunu nasıl değiştirdiğini inceleyin.

## Varsayımı zorlayın

Beklenen hücre sayılarını 5'in altına düşüren bir tablo kurun; Pearson ve kesin test sonuçlarını yön ve koşullandırma seçimini değiştirmeden karşılaştırın.
