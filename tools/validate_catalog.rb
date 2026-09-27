# Run from al-folio-site: bundle exec ruby ../tools/validate_catalog.rb /path/to/built/site
require 'yaml'
require 'date'
require 'uri'
require 'json'
require 'nokogiri'

root = File.expand_path('..', __dir__)
site = File.join(root, 'al-folio-site')
output = File.expand_path(ARGV.fetch(0))
errors = []
load_yaml = ->(path) { YAML.safe_load(File.read(path), permitted_classes: [Date, Time], aliases: true) }
books = load_yaml.call(File.join(site, '_data/research_books.yml'))
packages = load_yaml.call(File.join(site, '_data/research_packages.yml'))
project_ids = load_yaml.call(File.join(site, '_data/research_projects.yml')).map { |p| p['id'] }.compact
Dir.glob(File.join(root, '.github/workflows/*.{yml,yaml}')).each { |p| load_yaml.call(p) }
load_yaml.call(File.join(site, '_config.yml'))
navigation = load_yaml.call(File.join(site, '_data/navigation.yml'))

[books, packages].each do |records|
  ids = records.map { |r| r.fetch('id') }
  errors << 'Duplicate catalogue IDs' unless ids.uniq == ids
  records.each do |record|
    errors << "Unsafe ID: #{record['id']}" unless record['id'].match?(/\A[a-zA-Z0-9-]+\z/)
    record.fetch('related_projects', []).each do |id|
      errors << "Unknown project #{id} in #{record['id']}" unless project_ids.include?(id)
    end
    record.fetch('verified_links', {}).each_value do |date|
      Date.iso8601(date.to_s)
    rescue ArgumentError
      errors << "Invalid verification date in #{record['id']}"
    end
  end
end
books.each do |book|
  %w[title title_en subtitle subtitle_en description description_en author language chapters status status_en].each do |field|
    errors << "Missing #{field} in #{book['id']}" if book[field].to_s.empty?
  end
  errors << "Invalid published flag in #{book['id']}" unless [true, false].include?(book['published'])
  public_formats = %w[site_url pdf_url epub_url source_url].select { |field| book[field] && book.dig('verified_links', field) }
  if book['published'] && public_formats.empty?
    errors << "Unverified published book: #{book['id']}"
  end
end
packages.each do |package|
  %w[name subtitle technologies].each do |field|
    errors << "Missing #{field} in #{package['id']}" if package[field].to_s.empty?
  end
  %w[tr en].each do |language|
    errors << "Missing #{language} description in #{package['id']}" if package.dig('description', language).to_s.empty?
    errors << "Missing #{language} status in #{package['id']}" if package.dig('docs', 'status', language).to_s.empty?
  end
  errors << "Invalid docs flag in #{package['id']}" unless [true, false].include?(package.dig('docs', 'published'))
  if package.dig('docs', 'published') && !package.dig('verified_links', 'docs')
    errors << "Unverified published package: #{package['id']}"
  end
end

cache = {}
read_html = ->(path) { cache[path] ||= Nokogiri::HTML(File.read(path)) }
pages = %w[index.html en/index.html books/index.html en/books/index.html software/index.html en/software/index.html research-projects/index.html en/projects/index.html]
pages.each do |path|
  file = File.join(output, path)
  unless File.file?(file)
    errors << "Missing page: #{path}"
    next
  end
  doc = read_html.call(file)
  language = path.start_with?('en/') ? 'en' : 'tr'
  errors << "Wrong language: #{path}" unless doc.at_css('html')['lang'] == language
  errors << "Unrendered Liquid: #{path}" if File.read(file).match?(/\{%|\{\{/)
  ids = doc.css('[id]').map { |node| node['id'] }
  errors << "Duplicate HTML IDs: #{path}" unless ids.uniq == ids
  errors << "Missing language alternative: #{path}" unless doc.at_css('link[rel="alternate"][hreflang]')
  errors << "Wrong primary navigation: #{path}" unless doc.css('.navbar-menu-list > .nav-item:not(.language-switcher)').count { |n| n.at_css('a, button.portal-nav-toggle') } == navigation.length
  doc.css('a[href]').each do |link|
    href = link['href']
    next if href.empty? || href == '#' || href.match?(/\A(?:https?:|mailto:|tel:|javascript:|\/\/)/)
    address, fragment = href.split('#', 2)
    address = URI::DEFAULT_PARSER.unescape(address.split('?', 2).first.to_s)
    target = if address.empty?
               file
             elsif address.start_with?('/')
               File.join(output, address.delete_prefix('/'))
             else
               File.expand_path(address, File.dirname(file))
             end
    target = File.join(target, 'index.html') if File.directory?(target)
    unless File.file?(target)
      errors << "Broken internal link #{path}: #{href}"
      next
    end
    if fragment && target.end_with?('.html') && !read_html.call(target).css('[id]').any? { |n| n['id'] == URI::DEFAULT_PARSER.unescape(fragment) }
      errors << "Missing anchor #{path}: #{href}"
    end
  end
  if path.end_with?('books/index.html')
    published_books = books.select { |book| book['published'] }
    errors << "Wrong book count: #{path}" unless doc.css('.book-card').length == published_books.length
    books.each do |book|
      card = doc.at_css("article##{book['id']}")
      errors << "Published book is missing: #{book['id']}" if book['published'] && card.nil?
      errors << "Unpublished book is visible: #{book['id']}" if !book['published'] && card
      next unless card
      if !book['published'] && !card.css('.package-card__link, .catalog-citation').empty?
        errors << "Unpublished book exposes publication links: #{book['id']}"
      end
    end
  end
  if path.end_with?('software/index.html')
    errors << "Wrong package count: #{path}" unless doc.css('.package-card').length == packages.length
    packages.each do |package|
      card = doc.at_css("article##{package['id']}")
      next unless card
      links = card.css('a').map { |a| a['href'] }
      if !package.dig('docs', 'published') && links.include?("https://byuzbasi.github.io#{package.dig('docs', 'path')}")
        errors << "Unpublished documentation linked: #{package['id']}"
      end
      if package['reference_url'] && !package.dig('verified_links', 'reference_url') && links.include?(package['reference_url'])
        errors << "Unverified manual linked: #{package['id']}"
      end
    end
  end
end
puts JSON.pretty_generate({ result: errors.empty? ? 'PASS' : 'FAIL', pages: pages.length, books: books.length, packages: packages.length, errors: errors.uniq })
exit(errors.empty? ? 0 : 1)
