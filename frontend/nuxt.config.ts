// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  ssr: false,
  alias: {
    "@/app/utils": "~/utils",
  },

  vite: {
    plugins: [tailwindcss() as any],
    resolve: {
      alias: {
        "@/app/utils": "/app/app/utils",
      },
    },
  },

  modules: [
    "@nuxtjs/google-fonts",
    "@nuxt/icon",
    "@pinia/nuxt",
    "shadcn-nuxt",
    "@nuxtjs/color-mode"
  ],

  shadcn: {
    prefix: '',
    componentDir: './app/components/ui'
  },

  colorMode: {
    classSuffix: ''
  },

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    public: {
      projectId: process.env.NUXT_PUBLIC_PROJECT_ID,
      apiBaseUrl:
        process.env.NUXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
      firebaseApiKey: process.env.NUXT_PUBLIC_FIREBASE_API_KEY || "",
      firebaseAuthDomain: process.env.NUXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
      firebaseProjectId: process.env.NUXT_PUBLIC_FIREBASE_PROJECT_ID || "",
      firebaseAppId: process.env.NUXT_PUBLIC_FIREBASE_APP_ID || "",
      firebaseMessagingSenderId:
        process.env.NUXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
      firebaseStorageBucket:
        process.env.NUXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
    },
  },

  app: {
    head: {
      title: "Trending News Finder — Find Viral Topics",
      meta: [
        {
          name: "description",
          content:
            "Discover trending topics from Reddit, Hacker News, Bluesky, and more.",
        },
      ],
      link: [
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        },
      ],
    },
  },
});
