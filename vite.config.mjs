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
        styles: 'frontend/main.css',
        favicon: 'frontend/favicon.ico',
        'dev-content': 'frontend/js/dev/dev-content.js',
        'payflow-create': 'frontend/js/welp_payflow/create.js',
        'payflow-success': 'frontend/js/welp_payflow/success.js',
      },
    },
  },
  plugins: [
    tailwindcss(),
    
    // vite-plugin-static-copy: Copia archivos estáticos durante el build
    // 
    // ¿Por qué es necesario?
    // - Vite solo incluye archivos que están importados en JS/CSS
    // - Las fuentes y favicon NO están importados en main.js, por lo que no se incluirían
    // - Este plugin asegura que se copien al directorio de salida
    //
    // Ventajas sobre alternativas:
    // - Dev server support: archivos disponibles en desarrollo sin build físico
    // - Más rápido que rollup-plugin-copy en desarrollo
    // - Control granular vs directorio public/ que copia todo
    //
    // Flujo:
    // frontend/fonts/ → static/dist/fonts/ → Django puede servirlas
    // frontend/favicon.ico → static/dist/favicon.ico → Django puede servirlo
    viteStaticCopy({
      targets: [
        {
          src: 'frontend/favicon.ico',  // Archivo origen
          dest: '.'                     // Destino: static/dist/ (raíz del outDir)
        },
        {
          src: 'frontend/fonts/**/*',   // Todas las fuentes y subdirectorios
          dest: 'fonts'                 // Destino: static/dist/fonts/
        }
      ]
    })
  ]
}); 