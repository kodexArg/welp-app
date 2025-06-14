import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  base: '/static/',
  server: {
    host: 'localhost',
    port: 5173,
    cors: true,
    origin: 'http://localhost:5173'
  },
  build: {
    manifest: 'manifest.json',
    outDir: 'static/dist',
    rollupOptions: {
      input: {
        main: 'frontend/main.js',
        favicon: 'frontend/favicon.ico',
      },
    },
  },
  plugins: [
    tailwindcss({
      config: './tailwind.config.js'
    }),
    
    // vite-plugin-static-copy: Copia archivos estáticos durante el build
    // 
    // ¿Por qué es necesario?
    // - Vite solo incluye archivos que están importados en JS/CSS
    // - El favicon.ico NO está importado en main.js, por lo que no se incluiría
    // - Este plugin asegura que se copie al directorio de salida
    //
    // Ventajas sobre alternativas:
    // - Dev server support: archivos disponibles en desarrollo sin build físico
    // - Más rápido que rollup-plugin-copy en desarrollo
    // - Control granular vs directorio public/ que copia todo
    //
    // Flujo:
    // frontend/favicon.ico → static/dist/favicon.ico → Django puede servirlo
    viteStaticCopy({
      targets: [
        {
          src: 'frontend/favicon.ico',  // Archivo origen
          dest: '.'                     // Destino: static/dist/ (raíz del outDir)
        }
      ]
    })
  ]
}); 