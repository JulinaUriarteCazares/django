import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // semantic.min.css ya viene minificado y trae un selector que lightningcss rechaza.
    cssMinify: false,
  },
})
