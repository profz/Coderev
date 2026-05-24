export default defineNuxtConfig({
  compatibilityDate: '2026-05-23',
  pages: true,
  ssr: false,
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
})
