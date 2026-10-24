# Static web handoff

Preparation only. No web host, public link or deployment was created.

1. Have the human host the backend first and verify its HTTPS health URL. Review the Beta/legal/provider/operational limits in PRODUCT_NOTES.md before public use.
2. From `mobileApp/mobile/`, compile the real HTTPS API origin (without a trailing slash):

   ```sh
   npm ci
   EXPO_PUBLIC_API_URL=https://YOUR_API_HOST npm run build:web
   ```

3. Upload the contents of `mobileApp/mobile/dist` to a static host. Include `_expo/`, fonts/assets, the root HTML, generated route HTML and nested settings files. The publish directory is `mobileApp/mobile/dist` when the host builds from the repository root.
4. Configure extensionless routes: `/week` serves `week.html`; `/settings/privacy` serves `settings/privacy.html`. Preserve real asset paths. If the host uses a single-page fallback, keep its index fallback after existing files. Do not point public hosting at `scripts/serve_web.py`; it is a localhost helper.
5. Set backend CORS_ORIGINS to the exact HTTPS web origin. Rebuild the app whenever EXPO_PUBLIC_API_URL changes; it is compiled public configuration. Provider keys, MODEL and JWT_SECRET remain on the backend.
6. In a fresh/private browser, check direct links, register/consent/screen/plan, sign in, all activities, proposal Accept/Decline, progress, JSON export, Stop and deletion. Check both phone and desktop widths. Repeat a separate live-provider check only when the human has configured and authorized it.
7. Share the generated host link only after these checks and the unresolved release requirements have been reviewed. This handoff does not represent public-service readiness or legal approval.
