import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    supportFile: false,
    specPattern: 'test/**/*.cy.ts',
    defaultCommandTimeout: 30000,
    requestTimeout: 30000,
    chromeWebSecurity: false,
    env: {
      apiUrl: 'http://localhost:8000'
    }
  },
  retries: {
    runMode: 2,
    openMode: 0
  }
})