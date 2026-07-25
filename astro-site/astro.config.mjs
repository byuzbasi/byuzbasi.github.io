import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://byuzbasi.github.io',
  output: 'static',
  publicDir: '../static',
  integrations: [sitemap()],
});
