---
layout: page
title: "R Programlama ve Paket Geliştirme · Uygulamalar"
permalink: /r-programlama/
lang: tr
nav: false
---

Yazar: **Prof. Dr. Bahadır Yüzbaşı**

R'yi ilk kez kullanan okurdan paket geliştirme, C++/Fortran arayüzleri ve CRAN bakımına uzanan 32 bölümün uygulama kodları. Kitap lisans, yüksek lisans ve doktora düzeyleri için hazırlanıyor. Bu sayfa kitabın yayımlanmış baskısı değil, sürümlü kod eşlikçisidir.

[Tam kod arşivi (ZIP)](/assets/r-programlama/2026-09-27/r-programlama-kodlar-2026-09-27.zip) · [SHA-256](/assets/r-programlama/2026-09-27/SHA256SUMS.txt) · [Dosya manifesti](/assets/r-programlama/2026-09-27/source/manifest.json)

Sürüm: 2026-09-27. Kodlar R 4.6.0 üzerinde küçük testlerle sınanmıştır. Her bölüm sayfası bağımlılıkları, çalıştırma komutunu ve beklenen sonucu açıklar. Bilerek hata üreten kitap parçalarını topluca çalıştırmayın; indirilebilir test girişlerini kullanın.

## Başlangıç

1. [R'yi kurun](https://cran.r-project.org/) ve tam kod arşivini açın.
2. Dizin yapısını değiştirmeden Bölüm 1 sayfasındaki komutu çalıştırın.
3. Bölümleri sırayla izleyin; ileri testler için belirtilen R paketlerini önceden kurun.

Betikler eksik bağımlılıkları otomatik kurmaz; GitHub'a gönderim veya CRAN başvurusu yapmaz. Bölüm 16'nın 64 tekrarlı örneği yalnız küçük bir öğretim sınamasıdır.

## Bölümler

| Bölüm | Konu ve kodlar |
| --- | --- |
| 1 | [R ile çalışmaya başlamak](/r-programlama/bolum-01/) |
| 2 | [Nesneler, değerler ve atomik vektörler](/r-programlama/bolum-02/) |
| 3 | [İndeksleme ve vektörleştirme](/r-programlama/bolum-03/) |
| 4 | [Bileşik veri yapıları](/r-programlama/bolum-04/) |
| 5 | [Dosyalar ve taşınabilir projeler](/r-programlama/bolum-05/) |
| 6 | [İfadeler ve akış denetimi](/r-programlama/bolum-06/) |
| 7 | [Fonksiyon tasarlamak](/r-programlama/bolum-07/) |
| 8 | [Ortamlar ve kapsam](/r-programlama/bolum-08/) |
| 9 | [Tembel değerlendirme](/r-programlama/bolum-09/) |
| 10 | [Koşullar ve hata ayıklama](/r-programlama/bolum-10/) |
| 11 | [Yineleme ve işlevsel programlama](/r-programlama/bolum-11/) |
| 12 | [Nesne sistemleri ve üstprogramlama](/r-programlama/bolum-12/) |
| 13 | [Veriyi dönüştürmek](/r-programlama/bolum-13/) |
| 14 | [Grafiklerle iletişim](/r-programlama/bolum-14/) |
| 15 | [Sayısal hesaplama ve rastgelelik](/r-programlama/bolum-15/) |
| 16 | [Simülasyonu doğru kurmak](/r-programlama/bolum-16/) |
| 17 | [Araştırma projesinin yaşamı](/r-programlama/bolum-17/) |
| 18 | [Araştırma kodundan güvenilir API'ye](/r-programlama/bolum-18/) |
| 19 | [Bir paketin tamamını ilk kez görmek](/r-programlama/bolum-19/) |
| 20 | [Paket anatomisi ve metadata](/r-programlama/bolum-20/) |
| 21 | [Belgeleme ve örnekler](/r-programlama/bolum-21/) |
| 22 | [Test tasarımı](/r-programlama/bolum-22/) |
| 23 | [Uzun biçimli belgeler](/r-programlama/bolum-23/) |
| 24 | [Kaynak paketi üretmek ve denetlemek](/r-programlama/bolum-24/) |
| 25 | [Önce ölçmek](/r-programlama/bolum-25/) |
| 26 | [Rcpp ile ilk çekirdek](/r-programlama/bolum-26/) |
| 27 | [RcppArmadillo ve dış kitaplıklar](/r-programlama/bolum-27/) |
| 28 | [R C API'sini anlamak](/r-programlama/bolum-28/) |
| 29 | [Modern Fortran'ı R'ye bağlamak](/r-programlama/bolum-29/) |
| 30 | [Yayıma aday sürüm](/r-programlama/bolum-30/) |
| 31 | [CRAN gönderimi ve geri bildirim](/r-programlama/bolum-31/) |
| 32 | [Bakımı yapılabilir bir paket](/r-programlama/bolum-32/) |

## Paket ve lisans

[BernoulliRuns kaynak deposu](https://github.com/byuzbasi/BernoulliRuns) ayrı bir paket adayıdır; burada CRAN kabulü iddia edilmez. sglasso vakası Bölüm 30–32'de kaynak kimliği ve bakım açısından ele alınır.

Özgün kodlar GPL-3.0-or-later lisanslıdır; [lisans bildirimi](/assets/r-programlama/2026-09-27/source/LICENSE.md). Üçüncü taraf malzemeler kendi lisanslarını korur. Kitap PDF'si bu kod arşivinde bulunmaz.
