/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090D16",
        surface: "#111827",
        surfaceElevated: "#1F2937",
        bullish: "#10B981",
        bearish: "#F43F5E",
        kronos: "#8B5CF6",
        kronosMuted: "#6D28D9",
        ghostGold: "#F59E0B"
      },
    },
  },
  plugins: [],
};
