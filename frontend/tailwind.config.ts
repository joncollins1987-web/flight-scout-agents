import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#f5f7fb",
        ink: "#0f1c2d",
        tide: "#0a5ea8",
        foam: "#d9ebff",
        signal: "#f7a600"
      },
      boxShadow: {
        card: "0 10px 30px rgba(15, 28, 45, 0.08)"
      }
    },
  },
  plugins: [],
};

export default config;
