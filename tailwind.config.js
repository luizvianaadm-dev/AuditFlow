/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#003366', // Azul Escuro Institucional
          light: '#004080',
          dark: '#00264d',
        },
        secondary: {
          DEFAULT: '#00AEEF', // Azul Claro Vibrante
          light: '#33beff',
          dark: '#008ecc',
        },
        background: '#F8FAFC',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
