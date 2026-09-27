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
profile:
  image: project-team/tubitak-1001-2026/bahadir-yuzbasi-card-v3.jpg
  image_alt: Prof. Dr. Bahadır Yüzbaşı portresi

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

<section class="academic-summary" aria-label="Araştırma profili">
  <p>İnönü Üniversitesi Ekonometri Bölümünde İstatistik ve Ekonometri Profesörüyüm. Araştırmalarım, yüksek boyutlu ve karmaşık verilerde güvenilir kestirim ve değişken seçimine odaklanıyor. Küçültme, ön-test ve penalize regresyon yöntemlerini istatistiksel öğrenme, uzamsal ve fonksiyonel veri analiziyle birleştiriyorum. Son çalışmalarımda ölçeklendirilmiş grup lasso ile değişken seçimini ve coğrafi ağırlıklı regresyonda küçültme kestirimini dijital platform fiyatlaması uygulamasıyla ele aldım.</p>
  <p>Yürütücüsü olduğum TÜBİTAK 1001 projesinde büyük mekânsal verilerdeki heterojenliği açıklanabilir makine öğrenmesiyle modellemeyi hedefliyoruz. Tamamlanan TÜBİTAK 3005 projemizde ise Van’ın göç dinamiklerini coğrafi ağırlıklı regresyonla inceledik. Kuramsal yöntemleri simülasyon, gerçek veri analizi ve R, Python, C++ ile geliştirilen yeniden üretilebilir araştırma araçlarıyla destekliyorum.</p>
</section>

<div class="profile-actions" aria-label="Hızlı erişim">
  <a class="profile-action profile-action--primary" href="#selected-publications">Seçilmiş yayınlar <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/research-projects/#tubitak-1001-buyuk-mekansal-veri' | relative_url }}">TÜBİTAK 1001 projesi <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/assets/files/Bahadir-Yuzbasi-CV.pdf' | relative_url }}" download>CV’yi indir <span aria-hidden="true">↓</span></a>
</div>

{% include academic-impact.liquid %}

{% include research-library.liquid %}

<section class="featured-works" aria-labelledby="featured-works-title">
  <p class="section-eyebrow">SEÇİLMİŞ ÇALIŞMALAR</p>
  <div class="featured-works__heading">
    <h2 id="featured-works-title">Kitaplar</h2>
    <a href="{{ '/publications/#books-title' | relative_url }}">Tüm kitaplar <span aria-hidden="true">→</span></a>
  </div>
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

  <div class="featured-works__heading featured-works__articles-title">
    <h2 id="selected-publications">Seçilmiş yayınlar</h2>
    <a href="{{ '/publications/' | relative_url }}">Tüm yayınlar <span aria-hidden="true">→</span></a>
  </div>
  <article class="featured-work featured-work--publications">
    <div class="featured-work__citation">{% bibliography --query @article[selected=true] %}</div>
  </article>
</section>
