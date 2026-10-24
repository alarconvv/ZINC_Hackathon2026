# ZINC mobile product build

Beta — content pending professional review. This build has had no clinical or legal review.

Work proceeds in plan order. Phase C is blocked until the Phase A/B end-to-end gate passes. The Streamlit app and its tests remain unchanged.

## Task record

- A1: scaffold the API and unchanged core bridge. Backend and unchanged Streamlit suites PASS.

- A2: add hashed accounts bearer tokens and login throttling. Backend and unchanged Streamlit suites PASS.

- A3: record explicit versioned health data consent. Backend and unchanged Streamlit suites PASS.

- A4: mirror profile screening and engine generated weekly plans. Backend and unchanged Streamlit suites PASS.

- A5: persist weekly scheduling activity logs and server safety locks. Backend and unchanged Streamlit suites PASS.

- A6: add bounded coach requests and explicit proposal acceptance. Backend and unchanged Streamlit suites PASS.

- A7: serve progress personal exports and complete account deletion. Backend and unchanged Streamlit suites PASS.

- A8: verify backend safety isolation persistence and all activity flows. Backend and unchanged Streamlit suites PASS.

## Expo runtime
Scaffold: Expo SDK 58 (expo ~58.0.19), React Native 0.88, TypeScript 6, Expo Router. Dependencies installed with expo install. SDK 58 transition: physical Expo Go clients must support SDK 58; otherwise use a development build. See https://docs.expo.dev/router/introduction/ .

- B1: scaffold Expo Router SDK 58 and typed secure API transport. Backend and unchanged Streamlit suites PASS.

- B2: build accessible aquatic design components and typography. Backend and unchanged Streamlit suites PASS.

- B3: connect accounts consent and one question safety onboarding. Backend and unchanged Streamlit suites PASS.

- B4: connect five tabs training coach proposals and progress board. Backend and unchanged Streamlit suites PASS.

## Cut-line gate
Above-cut-line browser gate PASS at 390×844 and 1280×900: UI register, consent and privacy link, seven-question safety screen, chosen days, plan, optional add/remove, twelve strength sets, unfinished Accept disabled, accepted next-week proposal, yoga, brain, relaxation, populated progress, rollover with reload, preferences, JSON download, Stop/423, deletion and Welcome. Offline coach fallback verified with provider credentials explicitly empty. No page errors or horizontal page overflow. Backend tests also verify stale safety messages override version conflicts. Phase C begins only after this gate and B5 commit.

- B5: finish account settings and verify the complete cut line. Backend and unchanged Streamlit suites PASS.

- C1: add contextual device local training reminders. Backend and unchanged Streamlit suites PASS.

- C1: test native reminder trigger mapping and time validation. Backend and unchanged Streamlit suites PASS.
