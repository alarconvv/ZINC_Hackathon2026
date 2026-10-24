import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./e2e',timeout:180000,workers:1,use:{baseURL:process.env.ZINC_WEB_URL||'http://127.0.0.1:8081',reducedMotion:'reduce',headless:true},reporter:'list',outputDir:'e2e/test-results'});
