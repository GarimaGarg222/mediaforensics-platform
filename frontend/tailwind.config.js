/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
        display: ["'Syne'", "sans-serif"],
      },
      colors: {
        brand: {
          50:  "#eefdf6",
          100: "#d6faea",
          200: "#b0f3d6",
          300: "#7ae8bb",
          400: "#3dd49a",
          500: "#1ab87e",
          600: "#0d9566",
          700: "#0c7854",
          800: "#0d5f44",
          900: "#0c4e39",
        },
        surface: {
          DEFAULT: "#0a0f0d",
          50:  "#f4f7f5",
          100: "#e8f0eb",
          200: "#c8d9ce",
          300: "#99bba5",
          400: "#629475",
          500: "#3f7558",
          600: "#2e5c43",
          700: "#264a37",
          800: "#1e3c2c",
          900: "#152a1f",
          950: "#0a0f0d",
        },
        danger: "#f05252",
        warn:   "#f59e0b",
      },
      animation: {
        "fade-up":   "fadeUp 0.4s ease forwards",
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "scan":      "scan 2s linear infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        scan: {
          "0%":   { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
    },
  },
  plugins: [],
}
