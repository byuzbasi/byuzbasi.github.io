---
layout: page
title: Projeler
permalink: /research-projects/
description: TÜBİTAK, üniversite ve uluslararası araştırma projeleri.
nav: true
nav_order: 3
---

<link rel="stylesheet" href="{{ '/assets/css/academic.css' | relative_url }}">

<section class="project-intro" aria-labelledby="project-intro-title">
  <p class="section-eyebrow">ARAŞTIRMA PORTFÖYÜ</p>
  <h1 id="project-intro-title">Projeler</h1>
  <p>TÜBİTAK, üniversite ve uluslararası araştırma bursları kapsamında; yüksek boyutlu veri, düzenlileştirme, fonksiyonel veri analizi ve mekânsal istatistik üzerine yürütülen çalışmalar.</p>
</section>

<section class="project-list" aria-label="Araştırma projeleri">
  {% for project in site.data.research_projects %}
    <article class="research-project">
      <div class="research-project__header">
        <p class="research-project__status">{{ project.status }}</p>
        <h2>{{ project.title }}</h2>
        <p class="research-project__funder">{{ project.funder }}</p>
      </div>
      <p class="research-project__focus">{{ project.focus }}</p>
      <dl class="research-project__facts">
        {% if project.number %}<div><dt>Proje no.</dt><dd>{{ project.number }}</dd></div>{% endif %}
        <div><dt>Dönem</dt><dd>{{ project.period }}</dd></div>
        <div><dt>Rol</dt><dd>{{ project.role }}</dd></div>
        <div><dt>Kurum</dt><dd>{{ project.institution }}</dd></div>
        {% if project.budget %}<div><dt>Destek</dt><dd>{{ project.budget }}</dd></div>{% endif %}
      </dl>
      {% if project.outputs %}
        <div class="research-project__outputs">
          <h3>İlişkili çıktılar</h3>
          <ul>{% for output in project.outputs %}<li>{{ output }}</li>{% endfor %}</ul>
        </div>
      {% endif %}
    </article>
  {% endfor %}
</section>
