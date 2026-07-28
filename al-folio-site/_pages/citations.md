---
layout: page
permalink: /citations/
title: Atıflar
description: OpenAlex üzerinden güncel atıf görünümü.
nav: true
nav_order: 2
---

<link rel="stylesheet" href="{{ '/assets/css/academic.css' | relative_url }}">

<div id="citation-summary" class="mb-4" aria-live="polite">Atıf verileri yükleniyor…</div>
<div id="citation-list"></div>

<script>
  (() => {
    const authorUrl = 'https://api.openalex.org/authors/orcid:0000-0002-6196-3201';
    const summary = document.getElementById('citation-summary');
    const list = document.getElementById('citation-list');
    const escapeHtml = (value) => String(value || '').replace(/[&<>'"]/g, (character) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));

    fetch(authorUrl)
      .then((response) => {
        if (!response.ok) throw new Error('OpenAlex yanıt vermedi');
        return response.json();
      })
      .then((author) => fetch(`https://api.openalex.org/works?filter=authorships.author.id:${author.id}&per-page=100&sort=cited_by_count:desc`)
        .then((response) => response.json())
        .then((works) => ({ author, works: works.results || [] })))
      .then(({ author, works }) => {
        summary.innerHTML = `<p><strong>${author.works_count}</strong> çalışma ve <strong>${author.cited_by_count}</strong> toplam atıf. ` +
          `<span class="text-muted">Kaynak: OpenAlex; sayfa her açıldığında yenilenir.</span></p>`;
        const rows = works.map((work) => {
          const url = work.doi || work.id;
          const year = work.publication_year || '—';
          return `<tr><td>${escapeHtml(work.display_name)}</td><td>${year}</td><td>${work.cited_by_count || 0}</td>` +
            `<td><a href="${escapeHtml(url)}" target="_blank" rel="noopener">Kayıt</a></td></tr>`;
        }).join('');
        list.innerHTML = `<div class="table-responsive"><table class="table table-sm">` +
          `<thead><tr><th>Yayın</th><th>Yıl</th><th>Atıf</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`;
      })
      .catch(() => {
        summary.innerHTML = '<p>Atıf verisi şu an yüklenemedi. Lütfen daha sonra tekrar deneyin veya Google Scholar profilini kullanın.</p>';
      });
  })();
</script>
