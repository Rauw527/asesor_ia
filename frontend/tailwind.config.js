/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        skin: {
          white: "#FFFFFF",
          cream: "#F9F6F1",
          beige: "#E8DFD4",
          sage: "#B7C4A7",
          "warm-gray": "#8A7C73",
        },
      },
    },
  },
  plugins: [],
}
