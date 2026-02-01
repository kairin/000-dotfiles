// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://kairin.github.io',
  base: '/000-dotfiles/',
  outDir: '../docs',
  vite: {
    plugins: [tailwindcss()],
  },
});
