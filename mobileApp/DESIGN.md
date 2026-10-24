---
name: ZINC mobile
description: An ocean-blue Expo extension for a clear, dated wellness week.
colors:
  blue: "#126bc5"
  ocean: "#063774"
  surface: "#f4faff"
  ink: "#12365b"
  muted: "#526b84"
  rule: "#d6e7f5"
  pale: "#e8f3ff"
  danger: "#a51d25"
  white: "#ffffff"
  danger-surface: "#fff7f7"
  light-meta: "#d5e9ff"
  sheet-backdrop: "#031f40aa"
typography:
  title:
    fontFamily: Manrope_700Bold
    fontSize: 30px
    fontWeight: 700
    lineHeight: 39px
  heading:
    fontFamily: Manrope_700Bold
    fontSize: 22px
    fontWeight: 700
    lineHeight: 30px
  body:
    fontFamily: DMSans_400Regular
    fontSize: 16px
    fontWeight: 400
    lineHeight: 25px
  body-large:
    fontFamily: DMSans_400Regular
    fontSize: 19px
    fontWeight: 400
    lineHeight: 29px
  label:
    fontFamily: DMSans_600SemiBold
    fontSize: 14px
    fontWeight: 600
  meta:
    fontFamily: DMSans_400Regular
    fontSize: 14px
  chip:
    fontFamily: DMSans_600SemiBold
    fontSize: 13px
  navigation:
    fontFamily: DMSans_600SemiBold
    fontSize: 12px
rounded:
  card: 24px
  button: 24px
  field: 16px
  chip: 16px
  movement: 20px
spacing:
  row-gap: 10px
  screen-padding: 20px
  screen-gap: 18px
  card-padding: 24px
  card-gap: 14px
  compact-padding: 14px
  compact-gap: 8px
components:
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.white}"
    rounded: "{rounded.button}"
    padding: 12px 20px
  button-secondary:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: 12px 20px
  button-danger:
    backgroundColor: "{colors.danger-surface}"
    textColor: "{colors.danger}"
    rounded: "{rounded.button}"
    padding: 12px 20px
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: 14px
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.card}"
    padding: 24px
  chip:
    backgroundColor: "{colors.pale}"
    textColor: "{colors.ink}"
    rounded: "{rounded.chip}"
    padding: 4px 12px
---

# Design System: ZINC mobile

## Overview

**Creative North Star: "A calm aquatic canvas"**

ZINC mobile extends the incumbent ocean-blue visual world into an Expo application for iOS, Android and web. Rich blue frames pale, rounded panels; clear type and factual counts make a dated week easy to follow. This document captures implemented source rather than a new visual direction. The root [DESIGN.md](../DESIGN.md) continues to describe the Streamlit fallback.

**Key Characteristics:**
- Ocean-blue framing with pale content surfaces.
- Rounded controls and readable, explicit labels.
- Completion and evidence presented with their meaning in words.
- Persistent Stop access and explicit acceptance of proposed changes.

## Colors

### Primary
Blue identifies primary actions and completed portions of rings and curves. Ocean anchors the shell and the lower end of the screen gradient. High contrast uses solid ocean for the screen background.

### Neutral
Surface holds detailed content. Ink carries body text; muted carries supporting text and field strokes. Rule marks ring tracks and the tab divider. Pale supports secondary actions and chips. White carries primary-button and on-blue title text; light-meta carries supporting text on blue.

### Safety
Danger supplies Stop text and its outline, paired with danger-surface. The translucent sheet-backdrop separates modal content from the underlying screen.

**The Meaning in Words Rule.** Status and evidence stay readable as text; color alone never supplies their meaning.

## Typography

**Display Font:** Manrope, loaded as Manrope_700Bold.
**Body Font:** DM Sans, loaded as DMSans_400Regular and DMSans_600SemiBold.

Titles introduce screens; headings organize pale cards; body text explains actions and records. Meta is a quieter supporting line, while SectionHeader uses semibold mixed-case text. The shell wordmark uses Manrope at 26; its Beta label is 13. These native family names are loaded in `src/app/_layout.tsx`; no explicit fallback family stack is defined.

`T` enables OS font scaling. The large-text preference changes its base size and line height; explicit component overrides still apply. Preserve that distinction when assessing large-text coverage.

## Layout

Screen content scrolls within 20-unit side padding, 48-unit bottom padding, an 18-unit vertical gap and a centered maximum width of 1040. The root header has a maximum width of 1080, horizontal padding 20, vertical padding 12 and a 10-unit gap. Values are React Native logical units; the frontmatter uses px for portable token representation.

Today uses wrapping summary cells with a 12-unit gap: below width 600, 47% flex bases produce two compact columns with 44-unit rings; wider screens use a 210-unit flex basis and 68-unit rings, giving four columns at the verified desktop viewport. This is a responsive wrap, not a guarantee of four columns at every width above 600.

Week is a dated agenda. Each card groups a 52-unit date block, activity title, text status, evidence, estimated minutes, optional Extra chip and a labeled reschedule icon. The action occupies its own row. Strength and yoga stack movement art above details below width 900; wider screens use a 40% art column. Art sits in a 260-unit-high panel.

Progress places a weekday/date/count rail beside the weekly completion context and an adjacent seven-column weekday/count row directly below the activity curve. The curve has a visible zero baseline and records completed activities by scheduled day. Keep those readable counts alongside the graphic.

## Elevation & Depth

The shared components define no shadows. Depth comes from the blue canvas, pale panels, white fields and modal backdrop. Sheets use a centered, scrollable card with maximum width 600 and no modal animation.

## Shapes

Cards and buttons share broad rounded corners; fields and chips use the tighter radius recorded above. Buttons have a three-unit border, transparent at rest except danger actions. Focus changes the button border to ink. Rings use a 100-unit SVG viewBox, radius 40, six-unit strokes and a round completion cap.

## Components

### Buttons
Primary, secondary and danger variants share a minimum height of 48. Pressed opacity is 0.78; focused borders use ink. Disabled controls use rule and muted; busy controls show an activity indicator and expose busy/disabled accessibility state. IconButton is 48 square with a 22-unit Feather icon, a focus border and a rule-colored pressed surface. No additional hover animation is implemented.

### Chips
Chip is a pale, text-bearing capsule. EvidenceBadge appends the word “evidence.” Week maps strength to Strong, brain to Emerging, and yoga/relaxation to Moderate. Train uses the returned item's badge for movement content. Preserve these distinctions rather than assigning one uniform evidence level.

### Cards / Containers
Card uses the surface token, standard padding and gap. Compact cards reduce padding/gap and grow to fill their summary cell. Row wraps with centered alignment and a 10-unit gap.

### Inputs / Fields
Input has a visible label, white background, one-unit muted border and minimum height 52. It enables font scaling and uses the label as its accessibility label. There is no custom focus/error styling in the shared Input. Check uses explicit checkbox semantics; Stepper composes labeled increase/decrease buttons with bounded disabled states.

### Navigation
Five bottom tabs pair Feather icons with Today, Week, Train, Coach and Progress labels. The surface tab bar has a rule divider, minimum height 78 and top/bottom padding 10/16. Active icons/text use blue; inactive ones use ink. The root SafeAreaView protects the top and sides.

### Stop and sheets
Once a plan exists, the root header exposes compact Stop. An unfinished active session replaces it with a full-width danger bar below the header, including chest pain, dizziness and faintness wording. Shared sheets also expose full Stop when a plan exists, above their scrolling card. Stop invokes the shared session action; stopped sessions route to the stopped screen.

### Completion rings and activity curve
Today ring percentages derive from returned done/total counts, with zero for a zero denominator, and show the count ratio. Progress uses the returned baseline completion percentage, with baseline totals, partials and extras stated separately. These are completion indicators, never a health score. The activity curve uses a zero baseline and scales against at least four completions; adjacent weekday/count text gives the actual values.

### Coach and training
Coach messages render through plain native Text, including proposal reasons; model text is not interpreted as Markdown, HTML or executable content. The returned last assistant reply reveals five characters per 20ms when reduced motion is off; reduced motion shows the full reply. Proposals have separate “Accept for next week” and “Decline — keep my plan” controls; acceptance is disabled when the server view disallows it. Preview alone does not alter the prescription.

Training presents the returned version, prescription and written cue beside movement reference art, with easier/harder examples as display chips. Logging, optional rest timer, self-reported relaxation completion and symptoms remain explicit. The completion card gives factual counts and next activity context.

## Do's and Don'ts

### Do:
- **Do** extend the incumbent ocean-blue canvas and pale rounded panels.
- **Do** keep weekday/count text adjacent to the curve and completion denominators visible.
- **Do** keep Stop accessible in the root header, active-session bar and shared sheets.
- **Do** use plain-text coach replies and explicit proposal acceptance.

### Don't:
- **Don't** describe a completion ring as a health score.
- **Don't** flatten Strong, Moderate and Emerging evidence into one badge level.
- **Don't** infer that a timer completes or records an activity automatically.

Documentation evidence: source inspection of the theme, shared components, root shell and all five tabs; the finish handoff reports four Playwright scenarios at 390×844 and 1280×900, with captures in `e2e/screenshots/`. A fresh reviewer closed the three original web findings concerning Today density, readable curve context and truthful Week evidence. This is a bounded web/source review, not full accessibility, native-device, clinical or legal certification. Native devices were unavailable. The visible Beta label and professional-review limits remain part of the product context.


## Weekly usability update

Onboarding presents a server-suggested week before the weekday controls, with recommended counts, rest-day guidance and explanations for optional extras. Today puts its server-selected next action above completion cards and distinguishes an overdue date from an upcoming date. Next-week rollover requires a dated confirmation and explains what happens to unstarted work. Week separates rescheduling, skipping and removing: removal is confirmed, recommendations remain visible, and started or finished records cannot be removed. Skip keeps partial work and does not mark it completed. Progress describes chosen-schedule completion in plain language. Coach labels live replies, fallback responses and pending proposals separately; optional rules previews and home-test records explain their purpose.
