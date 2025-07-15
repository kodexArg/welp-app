/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './frontend/js/**/*.js',
    './frontend/css/**/*.css', /* Incluye todos los archivos CSS */
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 