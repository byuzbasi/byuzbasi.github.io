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

I view statistics not as a way to eliminate uncertainty, but as a discipline that makes uncertainty measurable, interpretable and useful for decision-making. I am a Professor of Statistics in the Department of Econometrics at İnönü University.

My research centres on shrinkage, pretest and penalized estimation methods for high-dimensional data with strongly correlated structures. I extend these ideas to spatial and functional data, statistical learning and elastic shape analysis.

For me, a strong statistical method should be not only theoretically sound, but also computationally tractable, reproducible and connected to a substantive problem. I therefore develop theory alongside simulation studies, real-data analyses and open-source software in R, Python and C++.

My applications span economics, biometry, the social sciences and digital platforms, while pursuing a common objective: turning complex data into reliable, quantifiable insight.

<section class="research-software" aria-labelledby="research-software-title">
  <p class="section-eyebrow">RESEARCH SOFTWARE</p>
  <h2 id="research-software-title">R · Python · C++</h2>
  <p>R packages and high-performance computing with C++/RcppArmadillo; Python workflows for statistical computing, machine learning and reproducible research.</p>
  <a class="text-link" href="{{ '/en/software/' | relative_url }}">Explore software and packages →</a>
</section>

<section class="featured-works" aria-labelledby="featured-works-title">
  <p class="section-eyebrow">FEATURED WORK</p>
  <h2 id="featured-works-title">Books</h2>
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

  <h2 class="featured-works__articles-title">Selected publications</h2>
  <article class="featured-work featured-work--publications">
    <div class="featured-work__citation">{% bibliography --query @article[selected=true] %}</div>
  </article>
</section>
