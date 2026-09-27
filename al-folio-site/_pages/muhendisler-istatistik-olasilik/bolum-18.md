---
layout: page
title: "Bölüm 18: ANOVA ve deney tasarımı"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-18/"
description: "Grup ortalamaları ayrışmasını ve faktöriyel ana/etkileşim etkilerini deney tasarımı bağlamında incelemek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/18_anova_deney_tasarimi.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/18-anova-deney-tasarimi.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Grup ortalamaları ayrışmasını ve faktöriyel ana/etkileşim etkilerini deney tasarımı bağlamında incelemek.

## Veri ve birimler

Sentetik sıcaklık düzeyleri ve çekme dayanımı MPa; faktör düzeyleri kategoriktir.

## Yöntem

Tek yönlü ANOVA kareler ayrışması ve iki düzeyli faktöriyel etki karşıtlıkları hesaplanır.

## Varsayım kontrolleri

- Bağımsızlık randomizasyonla ilişkilendirilir; artık normalliği ve varyans dengesi incelenir.
- Ana etkilerin güçlü etkileşim varken tek başına yorumlanmaması gerektiği belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/18_anova_deney_tasarimi.py
BOOK_SMOKE=1 quarto render labs/r/18-anova-deney-tasarimi.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- ANOVA bileşenleri ve F testi
- Ana etki ve etkileşim tahminleri

## Yorum ve uygulama görevi

İstatistiksel farkı süreç ayarı kararına dönüştürürken hangi tanıların gerektiğini açıklayın.

Bir etkileşim senaryosu kurup yalnız ana etkilerle yapılan kararın nasıl yanıltıcı olabileceğini gösterin.

## Varsayımı zorlayın

Yarım kesirde ana etkiyi iki faktörlü etkileşimle karıştırın; foldover eklenince hangi etkilerin ayrılabildiğini işaret sütunlarıyla doğrulayın.
