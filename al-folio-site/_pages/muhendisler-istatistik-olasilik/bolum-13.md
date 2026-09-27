---
layout: page
title: "Bölüm 13: Güven, öngörü ve tolerans aralıkları"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-13/"
description: "Parametre, gelecek gözlem ve anakütle içeriği için kurulan aralıkların farklı hedeflerini ayırmak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/13_guven_araliklari.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/13-guven-araliklari.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Parametre, gelecek gözlem ve anakütle içeriği için kurulan aralıkların farklı hedeflerini ayırmak.

## Veri ve birimler

Sentetik kaplama kalınlığı ölçümleri mikrometre ve ikili uygunluk sayıları adettir.

## Yöntem

Ortalama için t güven aralığı, tek gözlem öngörü aralığı ve oran için Wilson aralığı hesaplanır.

## Varsayım kontrolleri

- Sürekli ölçümler için yaklaşık normallik ve bağımsızlık değerlendirilir.
- İkili sonuçlarda pay ile paydanın tutarlılığı denetlenir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/13_guven_araliklari.py
BOOK_SMOKE=1 quarto render labs/r/13-guven-araliklari.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Güven ve öngörü aralıklarının karşılaştırması
- Wilson oran aralığı

## Yorum ve uygulama görevi

Öngörü aralığının güven aralığından neden daha geniş olduğunu açıklayın.

Örneklem büyüklüğünü iki katına çıkarırken standart sapmayı sabit tutup iki aralığın genişliklerini karşılaştırın.

## Varsayımı zorlayın

Süreç ortalaması sabitken tek-parça varyansını artırın; güven ve öngörü aralığının şartname kararını neden farklı etkilediğini gösterin.
