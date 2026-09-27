---
layout: page
title: "Bölüm 10: Limit teoremleri ve Monte Carlo"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-10/"
description: "Küçük ve sabit tohumlu bir simülasyonla analitik sistem güvenilirliğini ve Monte Carlo hatasını karşılaştırmak."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/10_limit_teoremleri_monte_carlo.py) · [R laboratuvarı](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/10-limit-teoremleri-monte-carlo.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Küçük ve sabit tohumlu bir simülasyonla analitik sistem güvenilirliğini ve Monte Carlo hatasını karşılaştırmak.

## Veri ve birimler

Sentetik iki bileşenli paralel sistem; denemeler Bernoulli göstergeleri, güvenilirlik boyutsuzdur.

## Yöntem

Bağımsız bileşen durumları üretilir; başarı oranı analitik değer ve Monte Carlo standart hatasıyla karşılaştırılır.

## Varsayım kontrolleri

- Rastgele tohum ve tekrar sayısı kaydedilir.
- Bileşen bağımsızlığı ile özdeş dağılım varsayımları açıkça belirtilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/10_limit_teoremleri_monte_carlo.py
BOOK_SMOKE=1 quarto render labs/r/10-limit-teoremleri-monte-carlo.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Analitik ve benzetim güvenilirliği
- Monte Carlo standart hatası ve farkı

## Yorum ve uygulama görevi

Benzetim farkının örnekleme hatasıyla uyumlu olup olmadığını değerlendirin.

Tekrar sayısını dört katına çıkarma durumunda beklenen Monte Carlo standart hatasının nasıl değişeceğini hesaplayın.

## Varsayımı zorlayın

Tekrarlar arasında ortak çevre etkisi ekleyin; nominal tekrar sayısının neden etkin örnek büyüklüğü olmadığını, tam üretim çalıştırmadan gösterin.
