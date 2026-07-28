---
layout: page
permalink: /cv/
title: Akademik Geçmiş
nav: true
nav_order: 7
cv_format: rendercv # options: rendercv, jsonresume
description: Eğitim, atamalar, projeler ve seçilmiş akademik çıktılar.
---

{% assign profile = site.data.cv.cv %}
{% assign appointments = profile.sections["Akademik atamalar"] %}
{% assign education = profile.sections["Eğitim ve akademik unvanlar"] %}
{% assign funding = profile.sections["Projeler, burslar ve ödüller"] %}
{% assign software = profile.sections["Yazılım ve teknik yetkinlikler"] %}
{% assign memberships = profile.sections["Mesleki üyelikler"] %}
{% assign metrics = profile.sections["Bibliyometrik özet"] %}
{% assign interests = profile.sections["Araştırma alanları"] %}

<div class="cv-page">
  <section class="cv-profile" aria-labelledby="cv-profile-title">
    <div>
      <p class="section-eyebrow">AKADEMİK ÖZET</p>
      <h2 id="cv-profile-title">{{ profile.name }}</h2>
      <p class="cv-profile__label">{{ profile.label }}</p>
      <p class="cv-profile__summary">{{ profile.summary }}</p>
    </div>
    <dl class="cv-profile__contact">
      <div><dt>Üniversite</dt><dd>İnönü Üniversitesi</dd></div>
      <div><dt>E-posta</dt><dd><a href="mailto:{{ profile.email }}">{{ profile.email }}</a></dd></div>
      <div><dt>Konum</dt><dd>{{ profile.location }}</dd></div>
      <div><dt>Profiller</dt><dd><a href="https://orcid.org/{{ profile.social_networks[0].username }}" target="_blank" rel="noopener">ORCID</a> · <a href="https://scholar.google.com/citations?user={{ profile.social_networks[2].username }}" target="_blank" rel="noopener">Google Scholar</a> · <a href="https://github.com/{{ profile.social_networks[1].username }}" target="_blank" rel="noopener">GitHub</a></dd></div>
    </dl>
  </section>

  <section class="cv-section" id="akademik-atamalar" aria-labelledby="appointments-title">
    <h2 id="appointments-title">Akademik atamalar</h2>
    {% for entry in appointments %}
      <article class="cv-entry">
        <p class="cv-entry__dates">{{ entry.start_date }}{% if entry.end_date %} – {{ entry.end_date }}{% else %} – günümüz{% endif %}</p>
        <div class="cv-entry__content">
          <h3>{{ entry.position }}</h3>
          <p class="cv-entry__institution">{{ entry.company }}{% if entry.location %} · {{ entry.location }}{% endif %}</p>
          {% if entry.summary %}<p>{{ entry.summary }}</p>{% endif %}
          {% if entry.highlights %}<ul>{% for highlight in entry.highlights %}<li>{{ highlight }}</li>{% endfor %}</ul>{% endif %}
        </div>
      </article>
    {% endfor %}
  </section>

  <section class="cv-section" id="egitim-ve-akademik-unvanlar" aria-labelledby="education-title">
    <h2 id="education-title">Eğitim ve akademik unvanlar</h2>
    {% for entry in education %}
      <article class="cv-entry">
        <p class="cv-entry__dates">{{ entry.start_date }}{% if entry.end_date and entry.end_date != entry.start_date %} – {{ entry.end_date }}{% endif %}</p>
        <div class="cv-entry__content">
          <h3>{{ entry.studyType }}{% if entry.area %} · {{ entry.area }}{% endif %}</h3>
          <p class="cv-entry__institution">{{ entry.institution }}{% if entry.location %} · {{ entry.location }}{% endif %}</p>
          {% if entry.highlights %}<ul>{% for highlight in entry.highlights %}<li>{{ highlight }}</li>{% endfor %}</ul>{% endif %}
        </div>
      </article>
    {% endfor %}
  </section>

  <section class="cv-section" id="projeler-burslar-ve-oduller" aria-labelledby="funding-title">
    <h2 id="funding-title">Projeler, burslar ve ödüller</h2>
    {% for entry in funding %}
      <article class="cv-entry">
        <p class="cv-entry__dates">{{ entry.start_date }}{% if entry.end_date and entry.end_date != entry.start_date %} – {{ entry.end_date }}{% endif %}</p>
        <div class="cv-entry__content">
          <h3>{{ entry.name }}</h3>
          <p>{{ entry.summary }}</p>
        </div>
      </article>
    {% endfor %}
  </section>

  <section class="cv-section" id="yazilim-ve-teknik-yetkinlikler" aria-labelledby="software-title">
    <h2 id="software-title">Yazılım ve teknik yetkinlikler</h2>
    <div class="cv-compact-list">
      {% for entry in software %}<article><h3>{{ entry.name }}</h3><p>{{ entry.summary }}</p></article>{% endfor %}
    </div>
  </section>

  <section class="cv-section" id="mesleki-uyelikler" aria-labelledby="memberships-title">
    <h2 id="memberships-title">Mesleki üyelikler</h2>
    <div class="cv-compact-list">
      {% for entry in memberships %}<article><h3>{{ entry.name }}</h3><p>{{ entry.summary }}</p></article>{% endfor %}
    </div>
  </section>

  <section class="cv-section" id="bibliyometrik-ozet" aria-labelledby="metrics-title">
    <h2 id="metrics-title">Bibliyometrik özet</h2>
    <div class="cv-compact-list">
      {% for entry in metrics %}<article><h3>{{ entry.name }}</h3><p>{{ entry.summary }}</p></article>{% endfor %}
    </div>
  </section>

  <section class="cv-section" id="arastirma-alanlari" aria-labelledby="interests-title">
    <h2 id="interests-title">Araştırma alanları</h2>
    <ul class="cv-interests">{% for entry in interests %}<li>{{ entry.name }}</li>{% endfor %}</ul>
  </section>
</div>
