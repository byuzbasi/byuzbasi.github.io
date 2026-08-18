---
layout: about-bilingual
title: Hakkımda
permalink: /
lang: tr
translation_key: about
display_name: Prof. Dr. Bahadır Yüzbaşı
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

<section class="academic-hero" aria-label="İstatistik, ekonometri ve veri bilimi araştırma görseli">
  <div class="academic-hero__copy">
    <p class="academic-hero__eyebrow">İSTATİSTİK · EKONOMETRİ · VERİ BİLİMİ</p>
    <h2>Karmaşık verideki yapıyı görünür kılmak.</h2>
    <p>Yüksek boyutlu, uzamsal ve fonksiyonel veriler için güvenilir çıkarım, öğrenme ve öngörü.</p>
  </div>
  <img class="academic-hero__image" src="{{ '/assets/img/statistical-landscape.svg' | relative_url }}" alt="Küçültme yolları, fonksiyonel veri eğrileri ve uzamsal konturları birbirine bağlayan altın çizgiden oluşan istatistiksel kompozisyon">
</section>

İnönü Üniversitesi Ekonometri Bölümünde İstatistik Profesörüyüm. Yüksek boyutlu, uzamsal ve fonksiyonel veriler için küçültme, ön-test ve penalize kestirim yöntemleri geliştiriyor; bu yöntemleri istatistiksel öğrenme ve elastik şekil analiziyle birleştiriyorum.

Kuramsal sonuçları simülasyon, gerçek veri analizleri ve açık kaynaklı R, Python ve C++ yazılımlarıyla birlikte geliştiriyorum. Çalışmalarım ekonomi, biyometri, sosyal bilimler ve dijital platformlarda karmaşık veriden güvenilir, yorumlanabilir bilgi üretmeye odaklanıyor.

<div class="profile-actions" aria-label="Hızlı erişim">
  <a class="profile-action profile-action--primary" href="{{ '/publications/' | relative_url }}">Seçilmiş yayınlar <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/research-projects/#tubitak-1001-buyuk-mekansal-veri' | relative_url }}">TÜBİTAK 1001 projesi <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/assets/files/Bahadir-Yuzbasi-CV.pdf' | relative_url }}" download>CV’yi indir <span aria-hidden="true">↓</span></a>
</div>

{% include academic-impact.liquid %}

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
    <div class="featured-work__citation">{% bibliography --query @article[selected=true] %}</div>
  </article>
</section>
