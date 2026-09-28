import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A0D12",
        surface: "#11161D",
        paper: "#EDF1F7",
        muted: "#8D98AC",
        dim: "#56616F",
        accent: "#2DD4A7",
        accent2: "#7C6CFF",
        danger: "#F2637B",
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
