import { defineConfig } from "vite";
import { resolve } from "path";
import postcss from "./postcss.config";

export default defineConfig({
  root: "src",
  css: {
    postcss: "./postcss.config.js",
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "src/index.html"),
        about: resolve(__dirname, "src/about.html"),
        timeTendencies: resolve(__dirname, "src/stats/timeTendencies.html"),
        fairSport: resolve(__dirname, "src/stats/fairestSports.html"),
        yourSport: resolve(__dirname, "src/stats/yourSport.html"),
      },
    },
  },
  server: {
    open: false,
    host: true,
  },
});
