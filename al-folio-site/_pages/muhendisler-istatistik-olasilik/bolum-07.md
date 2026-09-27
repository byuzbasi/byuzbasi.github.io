---
layout: page
title: "Bölüm 7: Kesikli olasılık dağılımları"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-07/"
description: "Binom, Poisson ve geometrik modellerin olay mekanizmalarına göre nasıl seçildiğini göstermek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/07_kesikli_dagilimlar.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/07-kesikli-dagilimlar.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Binom, Poisson ve geometrik modellerin olay mekanizmalarına göre nasıl seçildiğini göstermek.

## Veri ve birimler

Sentetik hata sayıları ve başarı denemeleri; sayımlar adet, olasılıklar boyutsuzdur.

## Yöntem

Kütle ve sağ kuyruk olasılıkları analitik dağılım işlevleriyle hesaplanır.

## Varsayım kontrolleri

- Binom için deneme sayısı ve başarı olasılığının sabitliği değerlendirilir.
- Poisson için olay hızının sabit ve ayrık olayların yaklaşık bağımsız olduğu belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/07_kesikli_dagilimlar.py
BOOK_SMOKE=1 quarto render labs/r/07-kesikli-dagilimlar.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Dağılım bazında olasılık tablosu
- Kuyruk olasılığı karşılaştırması

## Yorum ve uygulama görevi

Aynı ortalamaya sahip modellerin kuyruk risklerinin neden farklı olabileceğini açıklayın.

Poisson hızını yüzde 20 artırıp en az beş hata olasılığındaki değişimi hesaplayın.

## Varsayımı zorlayın

Günlere göre değişen kusur olasılığıyla aşırı yayılım üretin; tek bir binom modelinin varyansını gözlenen günlük varyansla karşılaştırın.
