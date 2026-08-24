import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: "#FFFFFF",
        surfaceLight: "#F1F5F9",
        border: "#E2E8F0",
        borderLight: "#F1F5F9",
        textPrimary: "#0F172A",
        textMuted: "#64748B",
        
        // Semantic sensor accents
        temp: "#F43F5E",
        humidity: "#0891B2",
        tds: "#0284C7",
        moisture: "#059669",
        flow: "#3B82F6",
        pump: "#059669",
        warning: "#D97706",
        danger: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
