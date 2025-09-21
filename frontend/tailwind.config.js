/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        futuristic: ['"Inter"', 'ui-sans-serif', 'system-ui']
      },
      colors: {
        glass: 'rgba(255,255,255,0.05)'
      }
    }
  },
  plugins: []
}
