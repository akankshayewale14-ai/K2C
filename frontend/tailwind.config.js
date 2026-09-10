/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0D0F0E",
        surface: "#151916",
        forest: "#18382A",
        emerald: "#3D7A5F",
        "emerald-light": "#52A67A",
        cream: "#F0EDE6",
        stone: "#A09D96",
        muted: "#6B6864",
        line: "#222520",
        copper: "#B87333",
        amber: "#E8A22A",
        lake: "#4A7FA0",
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "sans-serif"],
        sans: ["Inter", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      maxWidth: {
        page: "1320px",
      },
    },
  },
  plugins: [],
};
