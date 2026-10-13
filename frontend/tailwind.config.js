const token = (name) => `rgb(var(--${name}) / <alpha-value>)`;

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      colors: {
        canvas: token("canvas"),
        card: token("card"),
        subtle: token("subtle"),
        line: token("line"),
        fg: token("fg"),
        muted: token("muted"),
        gold: token("gold"),
        accent: token("accent"),
        "accent-soft": token("accent-soft"),
        ok: token("ok"),
        warn: token("warn"),
        danger: token("danger"),
      },
      keyframes: {
        "fade-up": { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "none" } },
        shake: { "0%,100%": { transform: "translateX(0)" }, "20%,60%": { transform: "translateX(-4px)" }, "40%,80%": { transform: "translateX(4px)" } },
      },
      animation: {
        "fade-up": "fade-up .3s ease-out both",
        shake: "shake .4s ease-in-out",
      },
      boxShadow: {
        gold: "0 0 0 1px rgb(var(--gold) / 0.15), 0 4px 18px rgb(var(--gold) / 0.12)",
        card: "0 1px 2px rgb(var(--shadow) / 0.06), 0 4px 16px rgb(var(--shadow) / 0.06)",
      },
    },
  },
  plugins: [],
};
