import { test, expect, Page } from "@playwright/test";
import fs from "node:fs";
const api = process.env.ZINC_API_URL || "http://127.0.0.1:8000";
const button = (page: Page, name: string) =>
  page.getByRole("button", { name, exact: true });
async function tab(page: Page, name: string) {
  const target = page.getByRole("tab", { name, exact: true });
  await target.click();
  await expect(target).toHaveAttribute("aria-selected", "true");
  const heading: Record<string, string | RegExp> = {
    Today: /^Your day,/,
    Week: "Your week",
    Coach: "Your coach",
    Progress: "Your progress",
  };
  if (heading[name])
    await expect(
      page.getByRole("heading", { name: heading[name], exact: true }),
    ).toBeVisible();
}
async function idle(page: Page) {
  await expect(
    page.getByText("Saving or reviewing…", { exact: true }),
  ).toHaveCount(0);
}
async function createPlan(page: Page, email: string) {
  await page.goto("/");
  await button(page, "Create account").click();
  await page.getByLabel("First name", { exact: true }).fill("Avery");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page
    .getByLabel("Password", { exact: true })
    .fill("fictional-test-password");
  await button(page, "Create account").click();
  await button(page, "Read privacy information").click();
  await expect(
    page.getByText("Draft — pending legal review.", { exact: true }),
  ).toBeVisible();
  await button(page, "Go back").click();
  await page.getByRole("checkbox").click();
  await button(page, "Agree and continue").click();
  await button(page, "Continue to safety").click();
  for (let i = 0; i < 7; i++) {
    await expect(
      page.getByText(`Question ${i + 1} of 7`, { exact: true }),
    ).toBeVisible();
    await button(page, "No").click();
  }
  await button(page, "See my suggested week").click();
  await expect(
    page.getByRole("heading", { name: "Choose your days", exact: true }),
  ).toBeInViewport();
  await page.screenshot({
    path: `e2e/screenshots/usability-${page.viewportSize()!.width}-suggestion.png`,
  });
  await page
    .getByLabel("Start Monday (YYYY-MM-DD, optional)", { exact: true })
    .fill("2026-10-19");
  await expect(
    page.getByRole("heading", { name: "Your week at a glance" }),
  ).toBeVisible();
  await button(page, "strength Mon").click();
  await button(page, "strength Thu").click();
  await button(page, "Create my week").click();
  await idle(page);
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "Choose 2 baseline days for strength" })
      .last(),
  ).toBeInViewport();
  await button(page, "strength Mon").click();
  await button(page, "strength Thu").click();
  await button(page, "Create my week").click();
  await expect(
    page.getByText("Your day, Avery.", { exact: true }),
  ).toBeVisible();
  await button(page, "Got it").click();
}
for (const width of [390, 1280])
  test(`cut line full product at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await createPlan(page, `cut-${width}-${Date.now()}@example.com`);
    await idle(page);
    await expect(page.getByText("How ZINC works", { exact: true })).toHaveCount(
      0,
    );
    await page.screenshot({ path: `e2e/screenshots/final-${width}-today.png` });
    await tab(page, "Week");
    await button(page, "Add activity").click();
    await expect(
      button(page, "Stop — chest pain, dizziness or faintness"),
    ).toBeVisible();
    await button(page, "Sun").click();
    await button(page, "Save activity day").click();
    await idle(page);
    await expect(page.getByText("Extra", { exact: true })).toBeVisible();
    await button(page, "Manage Yoga 2026-10-25").click();
    await button(page, "Remove activity").click();
    await expect(
      page.getByText(/We recommend keeping your weekly activities/),
    ).toBeVisible();
    await button(page, "Remove from my schedule").click();
    await idle(page);
    await expect(page.getByText("Extra", { exact: true })).toHaveCount(0);
    await button(page, "Start activity").first().click();
    await expect(page.getByText("Sit to stand", { exact: true })).toBeVisible();
    await button(page, "Record set").click();
    await idle(page);
    await expect(
      button(page, "Stop — chest pain, dizziness or faintness"),
    ).toBeVisible();
    await page
      .getByRole("heading", { name: "Strength & balance", exact: true })
      .scrollIntoViewIfNeeded();
    await page.screenshot({ path: `e2e/screenshots/final-${width}-train.png` });
    await tab(page, "Coach");
    await page
      .getByRole("heading", { name: "Your coach", exact: true })
      .evaluate((el) => {
        for (let p = el.parentElement; p; p = p.parentElement) {
          if (getComputedStyle(p).overflowY === "auto") {
            p.scrollTop = 0;
            break;
          }
        }
      });
    await page.screenshot({
      path: `e2e/screenshots/final-${width}-coach-initial.png`,
    });
    await page.getByLabel("Ask your coach", { exact: true }).fill("Hello");
    await button(page, "Send message").click();
    await idle(page);
    await expect(
      page.getByText(/Coach unavailable — fallback response/),
    ).toBeVisible();
    await button(page, "Adjust without AI").click();
    await button(page, "Preview adjustment").click();
    await idle(page);
    await expect(button(page, "Accept for next week")).toBeDisabled();
    await button(page, "Accept for next week").scrollIntoViewIfNeeded();
    await page.screenshot({ path: `e2e/screenshots/final-${width}-coach.png` });
    await tab(page, "Train");
    for (let i = 0; i < 11; i++) {
      await button(page, "Record set").click();
      await idle(page);
    }
    await expect(
      page.getByText("12 sets recorded", { exact: true }),
    ).toBeVisible();
    await page.screenshot({
      path: `e2e/screenshots/cut-${width}-completion.png`,
      fullPage: true,
    });
    await tab(page, "Coach");
    await button(page, "Adjust without AI").click();
    await button(page, "harder").click();
    await button(page, "Preview adjustment").click();
    await idle(page);
    await button(page, "Accept for next week").click();
    await idle(page);
    await tab(page, "Week");
    for (const section of ["Yoga", "Brain games", "Relaxation"]) {
      const id =
        section === "Yoga"
          ? "yoga"
          : section === "Brain games"
            ? "brain"
            : "relaxation";
      await page
        .getByTestId(`activity-${id}-2026-10-20`)
        .getByRole("button", { name: "Start activity", exact: true })
        .click();
      if (section === "Yoga") {
        for (let i = 0; i < 5; i++) {
          await button(page, "Record pose").click();
          await idle(page);
        }
      } else if (section === "Brain games") {
        for (let i = 0; i < 5; i++) {
          await page.getByLabel("Your answer", { exact: true }).fill("0");
          await button(page, "Check answer").click();
          await idle(page);
        }
      } else {
        await button(page, "5 minutes").click();
        await button(page, "Done — record my minutes").click();
        await idle(page);
      }
      await expect(
        page.getByText("Nice work, Avery.", { exact: true }),
      ).toBeVisible();
      await tab(page, "Week");
    }
    await tab(page, "Progress");
    await expect(
      page.getByText("Relaxation: 5 minutes self-reported", { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("heading", { name: "Your progress", exact: true })
      .evaluate((el) => {
        for (let p = el.parentElement; p; p = p.parentElement) {
          if (getComputedStyle(p).overflowY === "auto") {
            p.scrollTop = 0;
            break;
          }
        }
      });
    await page.screenshot({
      path: `e2e/screenshots/cut-${width}-progress.png`,
      fullPage: true,
    });
    await page
      .getByRole("heading", { name: "Your activity rhythm", exact: true })
      .evaluate((el) => el.scrollIntoView({ block: "start" }));
    await page.screenshot({ path: `e2e/screenshots/final-${width}-curve.png` });
    await button(page, "Record a home test").click();
    await page.clock.install();
    await button(page, "30-second chair stands").click();
    await button(page, "Start home test").click();
    for (let i = 0; i < 3; i++)
      await button(page, "Count a chair stand").click();
    await page.clock.fastForward(31000);
    await button(page, "Save test result").click();
    await expect(
      page.getByText("Result saved. Your plan is unchanged.", { exact: true }),
    ).toBeVisible();
    await page.clock.resume();
    await button(page, "Back to Progress").click();
    await expect(
      page
        .getByText(/Chair stands: 3 stands/)
        .filter({ visible: true })
        .first(),
    ).toBeVisible();
    await page
      .getByRole("heading", { name: "Your scoreboard", exact: true })
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: `e2e/screenshots/final-${width}-scoreboard.png`,
    });
    await tab(page, "Today");
    await button(page, "Start next week").click();
    await expect(
      page.getByRole("heading", { name: "Review your next week", exact: true }),
    ).toBeVisible();
    await button(page, "Start week 2").scrollIntoViewIfNeeded();
    await expect(button(page, "Start week 2")).toBeInViewport();
    await page.screenshot({
      path: `e2e/screenshots/usability-${width}-next-week.png`,
    });
    await button(page, "Keep working on this week").click();
    await button(page, "Start next week").click();
    await button(page, "Start week 2").click();
    await idle(page);
    await expect(
      page.getByText(/Week 2 is ready, beginning 2026-10-26/),
    ).toBeInViewport();
    await page.reload();
    await expect(
      page
        .getByText(/Protect · Week 2/)
        .filter({ visible: true })
        .first(),
    ).toBeVisible();
    await expect(page.getByText("How ZINC works", { exact: true })).toHaveCount(
      0,
    );
    await expect(
      page
        .getByText(/Protect · Week 2/)
        .filter({ visible: true })
        .first(),
    ).toBeVisible();
    await button(page, "Settings").click();
    await page
      .getByRole("checkbox", { name: "Larger text", exact: true })
      .click();
    await page
      .getByRole("checkbox", { name: "High contrast", exact: true })
      .click();
    const downloadPromise = page.waitForEvent("download");
    await button(page, "Download my data").click();
    const download = await downloadPromise;
    const path = await download.path();
    const exported = JSON.parse(fs.readFileSync(path!, "utf8"));
    expect(exported.state.history.length).toBe(1);
    expect(exported.consents.length).toBe(1);
    expect(exported.state.home_tests.at(-1).value).toBe(3);
    await button(page, "Back to my week").click();
    await page
      .getByRole("heading", { name: /^Your day,/ })
      .scrollIntoViewIfNeeded();
    await button(page, "Stop").focus();
    await expect(button(page, "Stop")).toBeFocused();
    await page.screenshot({
      path: `e2e/screenshots/final-${width}-large-focus.png`,
    });
    await button(page, "Stop").click();
    await expect(
      page.getByText("Session stopped", { exact: true }),
    ).toBeVisible();
    const token = await page.evaluate(() =>
      localStorage.getItem("zinc-access-token"),
    );
    expect(
      (
        await page.request.post(api + "/activities/active/finish", {
          headers: { Authorization: `Bearer ${token}` },
          data: { skipped: true },
        })
      ).status(),
    ).toBe(423);
    await page.screenshot({
      path: `e2e/screenshots/cut-${width}-stopped.png`,
      fullPage: true,
    });
    await button(page, "Settings").click();
    await button(page, "Delete my account").click();
    await page
      .getByRole("checkbox", {
        name: "Delete my account permanently",
        exact: true,
      })
      .click();
    await button(page, "Confirm account deletion").click();
    await expect(
      page.getByRole("heading", {
        name: "Strength for the years ahead",
        exact: true,
      }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      ),
    ).toBe(false);
    expect(errors).toEqual([]);
  });

for (const width of [390, 1280])
  test(`fictional demo populated progress at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    const notes = fs.readFileSync("../PRODUCT_NOTES.md", "utf8"),
      password = notes.match(/Demo password: `([^`]+)`/)![1];
    await page.goto("/");
    await button(page, "Sign in").click();
    await page.getByLabel("Email", { exact: true }).fill("maria@demo.zinc");
    await page.getByLabel("Password", { exact: true }).fill(password);
    await button(page, "Sign in").click();
    await expect(
      page.getByText("Your day, Maria.", { exact: true }),
    ).toBeVisible();
    if (await button(page, "Got it").isVisible())
      await button(page, "Got it").click();
    await tab(page, "Week");
    await page.screenshot({ path: `e2e/screenshots/final-${width}-week.png` });
    await tab(page, "Progress");
    await expect(page.getByText("75%", { exact: true })).toBeVisible();
    await expect(
      page.getByText("Relaxation: 8 minutes self-reported", { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("heading", { name: "Your scoreboard", exact: true })
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: `e2e/screenshots/final-${width}-demo-progress.png`,
    });
    await button(page, "Settings").click();
    await button(page, "Sign out").click();
    await expect(
      page.getByRole("heading", {
        name: "Strength for the years ahead",
        exact: true,
      }),
    ).toBeVisible();
  });

for (const width of [390, 1280])
  test(`flexible week choices at ${width}`, async ({ page }) => {
    test.setTimeout(45000);
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    await createPlan(page, `flex-${width}-${Date.now()}@example.com`);
    await tab(page, "Week");
    const yoga = page.getByTestId("activity-yoga-2026-10-20");
    await button(page, "Manage Yoga 2026-10-20").click();
    await button(page, "Remove activity").click();
    await expect(
      page.getByText(/We recommend keeping your weekly activities/),
    ).toBeVisible();
    await button(page, "Remove from my schedule").scrollIntoViewIfNeeded();
    await expect(button(page, "Remove from my schedule")).toBeInViewport();
    await page.screenshot({
      path: `e2e/screenshots/usability-${width}-remove-warning.png`,
    });
    await button(page, "Keep activity").click();
    await button(page, "Close").click();
    await expect(yoga).toBeVisible();
    await button(page, "Manage Yoga 2026-10-20").click();
    await button(page, "Remove activity").click();
    await button(page, "Remove from my schedule").click();
    await idle(page);
    await expect(yoga).toHaveCount(0);
    await expect(
      page.getByText("Yoga: 1 scheduled · 2 recommended", { exact: true }),
    ).toBeVisible();
    await page.reload();
    await expect(yoga).toHaveCount(0);
    await button(page, "Manage Brain games 2026-10-20").click();
    await button(page, "Skip activity").click();
    await button(page, "Skip for this week").click();
    await idle(page);
    await expect(
      page
        .getByTestId("activity-brain-2026-10-20")
        .getByText("Skipped", { exact: true }),
    ).toBeVisible();
    await button(page, "Manage Brain games 2026-10-20").click();
    await expect(button(page, "Remove activity")).toHaveCount(0);
    await button(page, "Close").click();
    await button(page, "Add activity").click();
    await button(page, "Tue").click();
    await button(page, "Save activity day").click();
    await idle(page);
    await expect(
      page.getByText("Yoga: 2 scheduled · 2 recommended", { exact: true }),
    ).toBeVisible();
    await tab(page, "Progress");
    await expect(
      page.getByText(/You completed 0 of 7 scheduled baseline activities/),
    ).toBeVisible();
    await tab(page, "Today");
    await button(page, "Start next week").click();
    await expect(
      page.getByText("2026-10-26 to 2026-11-01", { exact: true }),
    ).toBeVisible();
    await button(page, "Keep working on this week").click();
    await expect(
      page.getByText(/Protect · Week 1/).filter({ visible: true }),
    ).toBeVisible();
    await button(page, "Settings").click();
    await button(page, "Delete my account").click();
    await page
      .getByRole("checkbox", {
        name: "Delete my account permanently",
        exact: true,
      })
      .click();
    await button(page, "Confirm account deletion").click();
    await expect(button(page, "Create account")).toBeVisible();
  });
