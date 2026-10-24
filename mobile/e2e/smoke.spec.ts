import { test, expect, Page } from "@playwright/test";
import fs from "node:fs";
const api = process.env.ZINC_API_URL || "http://127.0.0.1:8000";
const button = (page: Page, name: string) =>
  page.getByRole("button", { name, exact: true });
async function tab(page: Page, name: string) {
  await page.getByRole("tab", { name, exact: true }).click();
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
  await button(page, "Continue to focus").click();
  await page
    .getByLabel("Start Monday (YYYY-MM-DD, optional)", { exact: true })
    .fill("2026-10-19");
  await button(page, "strength Mon").click();
  await button(page, "strength Thu").click();
  await button(page, "Create my week").click();
  await expect(
    page.getByText("Your complete week, Avery.", { exact: true }),
  ).toBeVisible();
  await button(page, "Got it").click();
}
for (const width of [390, 1280])
  test(`cut line full product at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await createPlan(page, `cut-${width}-${Date.now()}@example.com`);
    await tab(page, "Week");
    await button(page, "Add activity").click();
    await button(page, "Sun").click();
    await button(page, "Save activity day").click();
    await idle(page);
    await expect(page.getByText("Extra", { exact: true })).toBeVisible();
    await button(page, "Reschedule Yoga 2026-10-25").click();
    await button(page, "Remove optional activity").click();
    await idle(page);
    await expect(page.getByText("Extra", { exact: true })).toHaveCount(0);
    await button(page, "Start activity").first().click();
    await expect(page.getByText("Sit to stand", { exact: true })).toBeVisible();
    await button(page, "Record set").click();
    await idle(page);
    await tab(page, "Coach");
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
    await page.screenshot({
      path: `e2e/screenshots/cut-${width}-progress.png`,
      fullPage: true,
    });
    await tab(page, "Today");
    await button(page, "Start next week").click();
    await idle(page);
    await page.reload();
    await expect(page.getByText(/Protect · Week 2/)).toBeVisible();
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
    await button(page, "Back to my week").click();
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
      page.getByText("Strength for the years ahead", { exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      ),
    ).toBe(false);
    expect(errors).toEqual([]);
  });
