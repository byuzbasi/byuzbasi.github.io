---
title: ''
date: 2026-07-25
type: landing

sections:
  - block: hero
    content:
      title: 'Prof. Dr. Bahadır Yüzbaşı'
      text: |-
        **İstatistik · Ekonometri · Veri Bilimi**

        Yüksek boyutlu veri, istatistiksel öğrenme ve düzenlileştirme yöntemleri üzerine araştırmalar yürütüyor; açık, yeniden üretilebilir ve etkisi ölçülebilir bilim üretmeye odaklanıyorum.
      cta:
        label: Yayınları incele
        url: '#yayinlar'
      cta_alt:
        label: Özgeçmişi indir
        url: '/uploads/Resume_Bahadir_Yuzbasi.pdf'
      cta_note:
        label: 'İnönü Üniversitesi · Uluslararası İstatistik Enstitüsü seçilmiş üyesi'
    design:
      background:
        color: '#0b1f33'
        text_color_light: true
      spacing:
        padding: ['6rem', '0', '5.5rem', '0']

  - block: about.biography
    id: hakkimda
    content:
      title: Akademik profil
      username: admin
    design:
      css_class: academic-about

  - block: markdown
    id: alanlar
    content:
      title: Araştırma alanları
      text: |-
        <div class="research-grid">
          <article><span>01</span><h3>Yüksek Boyutlu İstatistik</h3><p>Boyutluluk, değişken seçimi ve kararlı tahmin problemleri için yöntem geliştirme.</p></article>
          <article><span>02</span><h3>İstatistiksel Öğrenme</h3><p>Tahmin performansını ve yorumlanabilirliği birlikte ele alan modern öğrenme yaklaşımları.</p></article>
          <article><span>03</span><h3>Mekânsal Veri Analizi</h3><p>Bağımlılık yapıları ve konum bilgisini kullanan regresyon ve çıkarım modelleri.</p></article>
          <article><span>04</span><h3>Düzenlileştirme</h3><p>Ceza, shrinkage ve pretest temelli tahmincilerin kuramsal ve uygulamalı incelemesi.</p></article>
        </div>
    design:
      columns: '1'
      css_class: research-section

  - block: collection
    id: yayinlar
    content:
      title: Güncel yayınlar
      subtitle: Seçilmiş makaleler, kitap bölümleri ve akademik çalışmalar
      text: '[Tüm yayınlara göz at](/publication/)'
      count: 6
      filters:
        folders:
          - publication
        exclude_future: true
    design:
      columns: '2'
      view: citation

  - block: portfolio
    id: projeler
    content:
      title: Araştırma projeleri
      subtitle: TÜBİTAK ve uluslararası araştırma deneyimi
      filters:
        folders:
          - project
      default_button_index: 0
      buttons:
        - name: Tümü
          tag: '*'
        - name: TÜBİTAK
          tag: Tubitak
    design:
      columns: '1'
      view: showcase
      flip_alt_rows: true

  - block: collection
    id: dersler
    content:
      title: Dersler ve kaynaklar
      subtitle: Sunumlar, uygulama verileri, kodlar ve ders kayıtları
      text: '[Tüm ders materyallerine git](/kurs/)'
      count: 6
      filters:
        folders:
          - kurs
        exclude_future: true
      order: desc
    design:
      columns: '2'
      view: compact

  - block: experience
    id: deneyim
    content:
      title: Akademik deneyim
      date_format: '2006'
      items:
        - title: Ekonometri Doçenti
          company: İnönü Üniversitesi
          location: Malatya, Türkiye
          date_start: '2024-03-22'
          date_end: ''
        - title: İstatistik Profesörü
          company: İnönü Üniversitesi
          location: Malatya, Türkiye
          date_start: '2023-03-06'
          date_end: ''
        - title: Misafir Doçent
          company: The University of British Columbia
          location: Vancouver, Kanada
          date_start: '2019-02-15'
          date_end: '2019-08-15'
    design:
      columns: '2'

  - block: contact
    id: iletisim
    content:
      title: İletişim ve iş birliği
      text: |-
        Araştırma iş birlikleri, lisansüstü danışmanlık ve akademik proje önerileri için iletişime geçebilirsiniz.
      email: b.yzb@hotmail.com
      autolink: true
      form:
        provider: netlify
        netlify:
          captcha: false
    design:
      columns: '2'
---
