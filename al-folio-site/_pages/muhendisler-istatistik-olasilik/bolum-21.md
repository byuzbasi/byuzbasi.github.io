---
layout: page
title: "Bölüm 21: Zaman serileri ve stokastik süreçler"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-21/"
description: "Zamansal bağımlılığı AR(1) öngörüsü ve Markov durum geçişleriyle iki tamamlayıcı ölçekte incelemek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/21_zaman_serileri_stokastik.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/21-zaman-serileri-stokastik.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Zamansal bağımlılığı AR(1) öngörüsü ve Markov durum geçişleriyle iki tamamlayıcı ölçekte incelemek.

## Veri ve birimler

Sentetik süreç sapmaları fiziksel birimde ve makine durum olasılıkları boyutsuzdur; zaman sırası korunur.

## Yöntem

AR(1) tek adım öngörüsü ve sabit geçiş matrisiyle çok adımlı durum olasılıkları hesaplanır.

## Varsayım kontrolleri

- AR(1) parametresinin durağanlık bölgesinde olduğu denetlenir.
- Geçiş matrisi satırlarının 1'e toplandığı ve zamanla değişmediği kabulü belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/21_zaman_serileri_stokastik.py
BOOK_SMOKE=1 quarto render labs/r/21-zaman-serileri-stokastik.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- AR(1) öngörü tablosu
- Markov durum olasılıklarının adım bazında gelişimi

## Yorum ve uygulama görevi

Negatif ve pozitif seri bağımlılığın bakım tahminine etkisini karşılaştırın.

Geçiş matrisindeki arıza durumunda kalma olasılığını artırıp beş adımlık arıza olasılığını yeniden hesaplayın.

## Varsayımı zorlayın

Doğrulama döneminde bir rejim kayması oluşturun; rastgele bölme ile ileri-zincir doğrulamanın hata ölçülerini karşılaştırın.
