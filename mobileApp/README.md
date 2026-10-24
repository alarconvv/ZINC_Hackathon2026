# ZINC mobile and web

Expo SDK 58 / React Native 0.88 / TypeScript / Expo Router. The aquatic interface extends the existing ZINC design; see [DESIGN.md](DESIGN.md) and [PRODUCT_NOTES.md](PRODUCT_NOTES.md).

The mobile application, API, deployment configuration and documents live in this folder. The interface code is in `mobile/`, the API and saved local database are in `backend/`, and the unchanged rules and exercise assets are in `core/`. Deployment configuration is in `render.yaml`. Run the commands below from `mobileApp/` unless noted.

- [Build plan](CODEX_MOBILE_PRODUCT_PLAN.md)
- [Product notes and demo instructions](PRODUCT_NOTES.md)
- [API run guide](BACKEND_README.md)
- [Design guide](DESIGN.md)
- [Web deployment guide](DEPLOY_WEB.md)
- [Draft privacy policy](privacy.md) and [terms](terms.md)

Start the API first, then in a separate terminal:

```sh
cd mobile
npm ci
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npx expo start --web
```

The API URL is public configuration, compiled into the app. Never put provider keys or JWT secrets in `EXPO_PUBLIC_*` variables. For a physical phone, the API URL must be your computer's reachable LAN address or an HTTPS host, not the phone's localhost. See the phone handoff in PRODUCT_NOTES.md.

```sh
npm run typecheck
npm run lint
npm test
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm run build:web
```

`privacy.md` and `terms.md` are the draft sources. `npm run prepare:content` regenerates the bundled `content/legal.json`; the consistency test rejects drift. The build:web command performs this automatically. The direct `npx expo export --platform web` command also builds the checked-in bundle.

To serve the export locally from `mobileApp/`:

```sh
python3 mobile/scripts/serve_web.py
```

Open http://127.0.0.1:8081 . Stop any Metro/static process already using port 8081 first. The local static helper supports extensionless Expo routes; it is not a public production server.

With the API running, the fictional demo seeded and Gemini credentials unset for the offline test fixture:

```sh
cd mobile
npx playwright install chromium
npm run test:e2e
```

The smoke matrix uses disposable fictional accounts, exports their JSON, stops and deletes them, and signs in to the fictional demo for populated progress. Screenshots are in `e2e/screenshots/`. No live Gemini requests are part of this gate.

Native notifications are local-only, requested in context and hidden on web. Actual iOS/Android UI, keyboard behavior and notification delivery still require device checks. Beta — content pending professional review; legal pages remain drafts. Expo CLI dependency advisories are documented in PRODUCT_NOTES.md and need review before public builds.

For Expo Go on a phone, start the API on your computer's LAN interface and use that LAN address in EXPO_PUBLIC_API_URL, then run `npx expo start` and scan its QR code. Use a trusted network and an SDK-58-compatible client. The full H2 guide in PRODUCT_NOTES.md explains the transition/build limits. No signing, remote build or store submission has been performed.
