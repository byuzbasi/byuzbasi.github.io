---
layout: page
permalink: /publications/
title: Yayınlar
description: Hakemli makaleler, kitap bölümleri ve diğer akademik yayınlar.
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<section class="mb-5" aria-labelledby="openalex-publications-title">
  <h2 id="openalex-publications-title">Son yayınlar</h2>
  <p id="openalex-publications-status" class="text-muted">ORCID kaydından güncel yayınlar yükleniyor…</p>
  <ol id="openalex-publications" class="bibliography"></ol>
</section>

<div class="publications">

{% bibliography %}

</div>

<script>
  (() => {
    const status = document.getElementById('openalex-publications-status');
    const list = document.getElementById('openalex-publications');
    const escapeHtml = (value) => String(value || '').replace(/[&<>'"]/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));

    fetch('https://api.openalex.org/authors/orcid:0000-0002-6196-3201')
      .then((response) => {
        if (!response.ok) throw new Error('OpenAlex yanıt vermedi');
        return response.json();
      })
      .then((author) => fetch(`https://api.openalex.org/works?filter=authorships.author.id:${author.id}&per-page=12&sort=publication_date:desc`))
      .then((response) => response.json())
      .then((data) => {
        const works = data.results || [];
        status.textContent = 'ORCID ile eşleşen en güncel kayıtlar · Kaynak: OpenAlex.';
        list.innerHTML = works.map((work) => {
          const destination = work.doi || work.id;
          const venue = work.primary_location && work.primary_location.source ? work.primary_location.source.display_name : '';
          const date = work.publication_date || work.publication_year || '';
          const periodical = `${venue}${venue && date ? ', ' : ''}${date}`;
          return `<li><span class="title"><a href="${escapeHtml(destination)}" target="_blank" rel="noopener">${escapeHtml(work.display_name)}</a></span>` +
            `${periodical ? ` <span class="periodical">${escapeHtml(periodical)}</span>` : ''}` +
            ` <span class="links">· <a href="/citations/">${work.cited_by_count || 0} atıf</a></span></li>`;
        }).join('');
      })
      .catch(() => {
        status.textContent = 'Güncel yayınlar şu an yüklenemedi; aşağıdaki BibTeX arşivi kullanılabilir.';
      });
  })();
</script>
