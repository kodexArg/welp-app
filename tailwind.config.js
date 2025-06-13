/** @type {import('@tailwindcss/vite').Config} */
export default {
  content: [
    "./templates/**/*.{html,py,svelte}",
    "./components/**/*.{html,py,svelte,js}",
    "./frontend/**/*.{html,js,svelte}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 