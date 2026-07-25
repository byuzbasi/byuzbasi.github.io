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
  <h2 id="featured-works-title">Kitaplar ve makaleler</h2>
  <div class="featured-works__grid">
    {% assign selected_works = site.data.featured_works | where: "featured", true | sort: "order" %}
    {% for work in selected_works %}
      <article class="featured-work{% if work.kind == 'book' %} featured-work--book{% endif %}">
        <p class="featured-work__type">{{ work.type }}</p>
        <h3><a href="{{ work.url }}" target="_blank" rel="noopener">{{ work.title }}</a></h3>
        <p class="featured-work__authors">{{ work.authors }}</p>
        {% if work.description %}<p>{{ work.description }}</p>{% endif %}
        {% if work.doi_url %}<p class="featured-work__links"><a href="{{ work.doi_url }}" target="_blank" rel="noopener">Kitap DOI</a></p>{% endif %}
        {% if work.reviews %}
          <div class="featured-work__reviews">
            <p>Uluslararası dergi değerlendirmeleri</p>
            <ul>
              {% for review in work.reviews %}
                <li><a href="{{ review.url }}" target="_blank" rel="noopener">{{ review.journal }} — {{ review.reviewer }} ({{ review.year }})</a></li>
              {% endfor %}
            </ul>
          </div>
        {% endif %}
      </article>
    {% endfor %}
  </div>
</section>
