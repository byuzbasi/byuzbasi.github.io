---
layout: about-bilingual
title: About
permalink: /en/
lang: en
translation_key: about
display_name: Bahadır Yüzbaşı, PhD
subtitle: >
  Professor of Statistics and Econometrics · İnönü University<br>
  <em>Elected Member, International Statistical Institute (2023–)</em>
profile:
  image: project-team/tubitak-1001-2026/bahadir-yuzbasi-card-v3.jpg
  image_alt: Portrait of Bahadır Yüzbaşı
description: Bahadır Yüzbaşı is a Professor of Statistics and Econometrics working on high-dimensional inference, functional and spatial data analysis, and statistical learning.
keywords: Bahadır Yüzbaşı, statistics, econometrics, high-dimensional inference, functional data analysis, spatial statistics, machine learning

selected_papers: false
social: true

announcements:
  enabled: false
  scrollable: false
  limit: 3

latest_posts:
  enabled: false
---

<section class="academic-hero" aria-label="Research visual for statistics, econometrics and data science">
  <div class="academic-hero__copy">
    <p class="academic-hero__eyebrow">STATISTICS · ECONOMETRICS · DATA SCIENCE</p>
    <h2>Making structure visible in complex data.</h2>
    <p>Reliable inference, learning and prediction for high-dimensional, spatial and functional data.</p>
  </div>
  <img class="academic-hero__image" src="{{ '/assets/img/statistical-landscape.svg' | relative_url }}" alt="Statistical composition connecting shrinkage paths, functional data curves and spatial contours with a gold inferential thread">
</section>

<section class="academic-summary" aria-label="Research profile">
  <p>I am a Professor of Statistics and Econometrics in the Department of Econometrics at İnönü University. My research focuses on reliable estimation and variable selection for high-dimensional and complex data. I combine shrinkage, pretest and penalized regression methods with statistical learning and spatial and functional data analysis. My recent work examines variable selection with scaled group lasso and shrinkage estimation in geographically weighted regression, including an application to digital platform pricing.</p>
  <p>In the TÜBİTAK 1001 project I lead, we aim to model heterogeneity in big spatial data using explainable machine learning. In our completed TÜBİTAK 3005 project, we studied migration dynamics in Van using geographically weighted regression. I support theoretical methods with simulation, real-data analysis and reproducible research tools developed in R, Python and C++.</p>
</section>

<div class="profile-actions" aria-label="Quick access">
  <a class="profile-action profile-action--primary" href="#selected-publications">Selected publications <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/en/projects/#tubitak-1001-buyuk-mekansal-veri' | relative_url }}">TÜBİTAK 1001 project <span aria-hidden="true">→</span></a>
  <a class="profile-action" href="{{ '/assets/files/Bahadir-Yuzbasi-CV.pdf' | relative_url }}" download>Download CV <span aria-hidden="true">↓</span></a>
</div>

{% include academic-impact.liquid %}

{% include research-library.liquid %}

<section class="featured-works" aria-labelledby="featured-works-title">
  <p class="section-eyebrow">FEATURED WORK</p>
  <div class="featured-works__heading">
    <h2 id="featured-works-title">Books</h2>
    <a href="{{ '/en/publications/#books-title' | relative_url }}">All books <span aria-hidden="true">→</span></a>
  </div>
  <article class="featured-work featured-work--book">
    <div class="featured-work__citation">{% bibliography --query @book[selected=true] %}</div>
    {% assign book = site.data.featured_works.books.ahmed_post-shrinkage_2023 %}
    <p class="featured-work__links"><a href="{{ book.publisher_url }}" target="_blank" rel="noopener">Publisher page</a></p>
    <div class="featured-work__reviews">
      <p>Reviews in international journals</p>
      <ul>
        {% for review in book.reviews %}
          <li><a href="{{ review.url }}" target="_blank" rel="noopener">{{ review.journal }} — {{ review.reviewer }} ({{ review.year }})</a></li>
        {% endfor %}
      </ul>
    </div>
  </article>

  <div class="featured-works__heading featured-works__articles-title">
    <h2 id="selected-publications">Selected publications</h2>
    <a href="{{ '/en/publications/' | relative_url }}">All publications <span aria-hidden="true">→</span></a>
  </div>
  <article class="featured-work featured-work--publications">
    <div class="featured-work__citation">{% bibliography --query @article[selected=true] %}</div>
  </article>
</section>
