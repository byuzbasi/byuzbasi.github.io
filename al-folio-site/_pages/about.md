---
layout: about
title: Hakkımda
permalink: /
subtitle: >
  İstatistik ve Ekonometri Profesörü · İnönü Üniversitesi<br>
  <em>Uluslararası İstatistik Enstitüsü Seçilmiş Üyesi (2023–)</em>

selected_papers: false
social: true

announcements:
  enabled: false
  scrollable: false
  limit: 3

latest_posts:
  enabled: false
---

<link rel="stylesheet" href="{{ '/assets/css/academic.css' | relative_url }}">

<section class="academic-hero" aria-label="İstatistik, ekonometri ve veri bilimi araştırma görseli">
  <div class="academic-hero__copy">
    <p class="academic-hero__eyebrow">İSTATİSTİK · EKONOMETRİ · VERİ BİLİMİ</p>
    <h2>Belirsizlikten ölçülebilir içgörüye.</h2>
    <p>İstatistiksel çıkarım, makine öğrenmesi ve karmaşık veri yapıları için sağlam yöntemler.</p>
  </div>
  <img class="academic-hero__image" src="{{ '/assets/img/statistical-landscape.svg' | relative_url }}" alt="Kontur çizgileri, regresyon doğrusu ve veri noktalarından oluşan soyut istatistiksel peyzaj">
</section>

İnönü Üniversitesi Ekonometri Bölümünde İstatistik Profesörüyüm. Araştırmalarım yüksek boyutlu, uzamsal ve fonksiyonel veriler için **cezalı, küçültme ve ön-test kestirim yöntemleri** geliştirir. İstatistiksel öğrenme, fonksiyonel veri analizi, elastik şekil analizi ve yeniden üretilebilir bilimsel yazılım geliştirme çalışma alanlarım arasındadır.

Kuramsal yöntemleri simülasyon, gerçek veri analizi ve açık kaynaklı R/C++ yazılımlarıyla birleştiriyorum. Uygulamalar; ekonomi, biyometri, sosyal bilimler ve dijital platformlar gibi farklı alanlara uzanıyor.

Araştırma alanlarım: makine öğrenmesi, uzamsal istatistik, fonksiyonel veri analizi, yüksek boyutlu veri, penalize regresyon ve büyük veri analitiği.

Yayınlar sayfasındaki kayıtlar ana BibTeX dosyasından üretilir; her yayının ayrıntı görünümünde DOI, atıf ve dış veri tabanı bağlantılarına yer verilir.

<section class="research-software" aria-labelledby="research-software-title">
  <p class="section-eyebrow">ARAŞTIRMA YAZILIMI</p>
  <h2 id="research-software-title">R · Python · C++</h2>
  <p>R paketleri, C++/RcppArmadillo ile yüksek performanslı hesaplama; Python ile istatistiksel hesaplama, makine öğrenmesi ve yeniden üretilebilir araştırma iş akışları.</p>
  <a class="text-link" href="{{ '/software/' | relative_url }}">Yazılım ve paketleri incele →</a>
</section>

<section class="featured-works" aria-labelledby="featured-works-title">
  <p class="section-eyebrow">SEÇİLMİŞ ÇALIŞMALAR</p>
  <h2 id="featured-works-title">Kitaplar</h2>
  <article class="featured-work featured-work--book">
    <div class="featured-work__citation">{% bibliography --query @book[selected=true] %}</div>
    {% assign book = site.data.featured_works.books.ahmed_post-shrinkage_2023 %}
    <p class="featured-work__links"><a href="{{ book.publisher_url }}" target="_blank" rel="noopener">Yayınevi sayfası</a></p>
    <div class="featured-work__reviews">
      <p>Uluslararası dergi değerlendirmeleri</p>
      <ul>
        {% for review in book.reviews %}
          <li><a href="{{ review.url }}" target="_blank" rel="noopener">{{ review.journal }} — {{ review.reviewer }} ({{ review.year }})</a></li>
        {% endfor %}
      </ul>
    </div>
  </article>

  <h2 class="featured-works__articles-title">Seçilmiş yayınlar</h2>
  <article class="featured-work featured-work--publications">
    <div class="featured-work__citation">{% bibliography --query @*[selected=true] %}</div>
  </article>
</section>
