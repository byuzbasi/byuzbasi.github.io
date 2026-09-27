---
layout: page
title: "Bölüm 19: İstatistiksel süreç kontrolü ve yeterlilik"
permalink: "/books/muhendisler-istatistik-olasilik/bolum-19/"
description: "Kontrol sınırlarını şartname sınırlarından ayırmak ve süreç yeterliliğinin kararlılık koşuluna bağlılığını göstermek."
nav: false
---

Prof. Dr. Bahadır Yüzbaşı · v1.1 · [Bütün bölümler](/books/muhendisler-istatistik-olasilik/)

[Python dosyası](/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/python/19_surec_kontrolu.py) · [R laboratuvarı](https://raw.githubusercontent.com/byuzbasi/byuzbasi.github.io/main/al-folio-site/assets/books/muhendisler-istatistik-olasilik/v1.1/labs/r/19-surec-kontrolu.qmd) · [Tam paket](/assets/books/muhendisler-istatistik-olasilik/v1.1/muhendisler-istatistik-olasilik-v1.1.zip)

## Amaç

Kontrol sınırlarını şartname sınırlarından ayırmak ve süreç yeterliliğinin kararlılık koşuluna bağlılığını göstermek.

## Veri ve birimler

Sentetik alt grup ölçümleri; ürün özelliği fiziksel birimde, yeterlilik indisleri boyutsuzdur.

## Yöntem

Referans süreç parametreleriyle kontrol sınırları ve şartname bilgisiyle yeterlilik indisleri hesaplanır.

## Varsayım kontrolleri

- Zamansal sıra korunur ve özel neden sinyalleri incelenir.
- Yeterlilik hesabından önce sürecin kararlı olduğu değerlendirilir.

## Çalıştırma

Önce tam paketi açın ve aşağıdaki yolu kendi klasörünüzle değiştirin. Tek dosya indirmek ortak yardımcıları sağlamaz.

```bash
cd "/absolute/path/muhendisler-istatistik-olasilik-v1.1"
BOOK_SMOKE=1 python3 labs/python/19_surec_kontrolu.py
BOOK_SMOKE=1 quarto render labs/r/19-surec-kontrolu.qmd --to html
```

Bu komutlar kısa deneme içindir; simülasyonlarda 64 tekrar kullanılır. Kurulum ve ortam bilgisi [çalıştırma rehberindedir](/assets/books/muhendisler-istatistik-olasilik/v1.1/README.md).

## Beklenen çıktılar

- Kontrol çizelgesi sınır ve sinyal tablosu
- Yeterlilik duyarlılık özeti

## Yorum ve uygulama görevi

Kontrol altında olmanın neden şartnameyi karşılama anlamına gelmediğini açıklayın.

Süreç ortalamasını hedefe kaydırıp Cp ve Cpk üzerindeki farklı etkileri hesaplayın.

## Varsayımı zorlayın

Yeni yüksek gözlemleri kullanarak kontrol sınırlarını sürekli güncelleyin; sinyalin dondurulmuş Faz II sınırına göre nasıl maskelendiğini gösterin.
