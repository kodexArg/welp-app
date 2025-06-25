// vite.config.mjs
import { defineConfig } from "file:///C:/Users/gcave/Projects/Dev/welp-app/node_modules/vite/dist/node/index.js";
import { viteStaticCopy } from "file:///C:/Users/gcave/Projects/Dev/welp-app/node_modules/vite-plugin-static-copy/dist/index.js";
import tailwindcss from "file:///C:/Users/gcave/Projects/Dev/welp-app/node_modules/@tailwindcss/vite/dist/index.mjs";
var vite_config_default = defineConfig({
  base: "/static/",
  server: {
    host: "localhost",
    port: 5173,
    cors: true,
    origin: "http://localhost:5173"
  },
  build: {
    manifest: "manifest.json",
    outDir: "static/dist",
    rollupOptions: {
      input: {
        main: "frontend/main.js",
        styles: "frontend/main.css",
        favicon: "frontend/favicon.ico"
      }
    }
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
          src: "frontend/favicon.ico",
          // Archivo origen
          dest: "."
          // Destino: static/dist/ (raíz del outDir)
        },
        {
          src: "frontend/fonts/**/*",
          // Todas las fuentes y subdirectorios
          dest: "fonts"
          // Destino: static/dist/fonts/
        }
      ]
    })
  ]
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcubWpzIl0sCiAgInNvdXJjZXNDb250ZW50IjogWyJjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZGlybmFtZSA9IFwiQzpcXFxcVXNlcnNcXFxcZ2NhdmVcXFxcUHJvamVjdHNcXFxcRGV2XFxcXHdlbHAtYXBwXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxnY2F2ZVxcXFxQcm9qZWN0c1xcXFxEZXZcXFxcd2VscC1hcHBcXFxcdml0ZS5jb25maWcubWpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9Vc2Vycy9nY2F2ZS9Qcm9qZWN0cy9EZXYvd2VscC1hcHAvdml0ZS5jb25maWcubWpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSc7XG5pbXBvcnQgeyB2aXRlU3RhdGljQ29weSB9IGZyb20gJ3ZpdGUtcGx1Z2luLXN0YXRpYy1jb3B5JztcbmltcG9ydCB0YWlsd2luZGNzcyBmcm9tICdAdGFpbHdpbmRjc3Mvdml0ZSc7XG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIGJhc2U6ICcvc3RhdGljLycsXG4gIHNlcnZlcjoge1xuICAgIGhvc3Q6ICdsb2NhbGhvc3QnLFxuICAgIHBvcnQ6IDUxNzMsXG4gICAgY29yczogdHJ1ZSxcbiAgICBvcmlnaW46ICdodHRwOi8vbG9jYWxob3N0OjUxNzMnXG4gIH0sXG4gIGJ1aWxkOiB7XG4gICAgbWFuaWZlc3Q6ICdtYW5pZmVzdC5qc29uJyxcbiAgICBvdXREaXI6ICdzdGF0aWMvZGlzdCcsXG4gICAgcm9sbHVwT3B0aW9uczoge1xuICAgICAgaW5wdXQ6IHtcbiAgICAgICAgbWFpbjogJ2Zyb250ZW5kL21haW4uanMnLFxuICAgICAgICBzdHlsZXM6ICdmcm9udGVuZC9tYWluLmNzcycsXG4gICAgICAgIGZhdmljb246ICdmcm9udGVuZC9mYXZpY29uLmljbycsXG4gICAgICB9LFxuICAgIH0sXG4gIH0sXG4gIHBsdWdpbnM6IFtcbiAgICB0YWlsd2luZGNzcygpLFxuICAgIFxuICAgIC8vIHZpdGUtcGx1Z2luLXN0YXRpYy1jb3B5OiBDb3BpYSBhcmNoaXZvcyBlc3RcdTAwRTF0aWNvcyBkdXJhbnRlIGVsIGJ1aWxkXG4gICAgLy8gXG4gICAgLy8gXHUwMEJGUG9yIHF1XHUwMEU5IGVzIG5lY2VzYXJpbz9cbiAgICAvLyAtIFZpdGUgc29sbyBpbmNsdXllIGFyY2hpdm9zIHF1ZSBlc3RcdTAwRTFuIGltcG9ydGFkb3MgZW4gSlMvQ1NTXG4gICAgLy8gLSBMYXMgZnVlbnRlcyB5IGZhdmljb24gTk8gZXN0XHUwMEUxbiBpbXBvcnRhZG9zIGVuIG1haW4uanMsIHBvciBsbyBxdWUgbm8gc2UgaW5jbHVpclx1MDBFRGFuXG4gICAgLy8gLSBFc3RlIHBsdWdpbiBhc2VndXJhIHF1ZSBzZSBjb3BpZW4gYWwgZGlyZWN0b3JpbyBkZSBzYWxpZGFcbiAgICAvL1xuICAgIC8vIFZlbnRhamFzIHNvYnJlIGFsdGVybmF0aXZhczpcbiAgICAvLyAtIERldiBzZXJ2ZXIgc3VwcG9ydDogYXJjaGl2b3MgZGlzcG9uaWJsZXMgZW4gZGVzYXJyb2xsbyBzaW4gYnVpbGQgZlx1MDBFRHNpY29cbiAgICAvLyAtIE1cdTAwRTFzIHJcdTAwRTFwaWRvIHF1ZSByb2xsdXAtcGx1Z2luLWNvcHkgZW4gZGVzYXJyb2xsb1xuICAgIC8vIC0gQ29udHJvbCBncmFudWxhciB2cyBkaXJlY3RvcmlvIHB1YmxpYy8gcXVlIGNvcGlhIHRvZG9cbiAgICAvL1xuICAgIC8vIEZsdWpvOlxuICAgIC8vIGZyb250ZW5kL2ZvbnRzLyBcdTIxOTIgc3RhdGljL2Rpc3QvZm9udHMvIFx1MjE5MiBEamFuZ28gcHVlZGUgc2VydmlybGFzXG4gICAgLy8gZnJvbnRlbmQvZmF2aWNvbi5pY28gXHUyMTkyIHN0YXRpYy9kaXN0L2Zhdmljb24uaWNvIFx1MjE5MiBEamFuZ28gcHVlZGUgc2VydmlybG9cbiAgICB2aXRlU3RhdGljQ29weSh7XG4gICAgICB0YXJnZXRzOiBbXG4gICAgICAgIHtcbiAgICAgICAgICBzcmM6ICdmcm9udGVuZC9mYXZpY29uLmljbycsICAvLyBBcmNoaXZvIG9yaWdlblxuICAgICAgICAgIGRlc3Q6ICcuJyAgICAgICAgICAgICAgICAgICAgIC8vIERlc3Rpbm86IHN0YXRpYy9kaXN0LyAocmFcdTAwRUR6IGRlbCBvdXREaXIpXG4gICAgICAgIH0sXG4gICAgICAgIHtcbiAgICAgICAgICBzcmM6ICdmcm9udGVuZC9mb250cy8qKi8qJywgICAvLyBUb2RhcyBsYXMgZnVlbnRlcyB5IHN1YmRpcmVjdG9yaW9zXG4gICAgICAgICAgZGVzdDogJ2ZvbnRzJyAgICAgICAgICAgICAgICAgLy8gRGVzdGlubzogc3RhdGljL2Rpc3QvZm9udHMvXG4gICAgICAgIH1cbiAgICAgIF1cbiAgICB9KVxuICBdXG59KTsgIl0sCiAgIm1hcHBpbmdzIjogIjtBQUE0UyxTQUFTLG9CQUFvQjtBQUN6VSxTQUFTLHNCQUFzQjtBQUMvQixPQUFPLGlCQUFpQjtBQUV4QixJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixNQUFNO0FBQUEsRUFDTixRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixRQUFRO0FBQUEsRUFDVjtBQUFBLEVBQ0EsT0FBTztBQUFBLElBQ0wsVUFBVTtBQUFBLElBQ1YsUUFBUTtBQUFBLElBQ1IsZUFBZTtBQUFBLE1BQ2IsT0FBTztBQUFBLFFBQ0wsTUFBTTtBQUFBLFFBQ04sUUFBUTtBQUFBLFFBQ1IsU0FBUztBQUFBLE1BQ1g7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsWUFBWTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBLElBaUJaLGVBQWU7QUFBQSxNQUNiLFNBQVM7QUFBQSxRQUNQO0FBQUEsVUFDRSxLQUFLO0FBQUE7QUFBQSxVQUNMLE1BQU07QUFBQTtBQUFBLFFBQ1I7QUFBQSxRQUNBO0FBQUEsVUFDRSxLQUFLO0FBQUE7QUFBQSxVQUNMLE1BQU07QUFBQTtBQUFBLFFBQ1I7QUFBQSxNQUNGO0FBQUEsSUFDRixDQUFDO0FBQUEsRUFDSDtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
