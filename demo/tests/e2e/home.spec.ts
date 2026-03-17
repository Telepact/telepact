import { expect, test } from "@playwright/test";

test.describe("Telepact todo demo", () => {
  test("renders seeded data from the full stack", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByText("Telepact Full-Stack Demo")).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Polish onboarding copy" })).toBeVisible();
    await expect(page.getByRole("heading", { level: 3, name: "Upload vendor tax forms" })).toBeVisible();
    await expect(page.getByText("Java service digest of the todo graph.")).toBeVisible();
    await expect(page.getByText("Cross-project pressure snapshot.")).toBeVisible();
  });

  test("can create, edit, complete, and delete a todo", async ({ page }) => {
    await page.goto("/");

    const composer = page.locator(".todoForm");
    await composer.getByLabel("Title").fill("Prepare board memo");
    await composer.getByLabel("Description").fill("Draft the updated board memo with Telepact findings.");
    await composer.getByLabel("Project").fill("Strategy");
    await composer.getByLabel("Tags").fill("board, writing");
    await page.getByRole("button", { name: "Add task" }).click();

    await expect(page.getByRole("heading", { level: 3, name: "Prepare board memo" })).toBeVisible();

    const newCard = page.locator(".todoCard", { hasText: "Prepare board memo" });
    await newCard.getByRole("button", { name: "Edit" }).click();
    await composer.getByLabel("Title").fill("Prepare board memo v2");
    await page.getByRole("button", { name: "Save task" }).click();

    await expect(page.getByRole("heading", { level: 3, name: "Prepare board memo v2" })).toBeVisible();

    const updatedCard = page.locator(".todoCard", { hasText: "Prepare board memo v2" });
    await updatedCard.getByRole("button", { name: "Done" }).click();
    await page.getByLabel("Status filter").selectOption("completed");
    await expect(page.getByRole("heading", { level: 3, name: "Prepare board memo v2" })).toBeVisible();

    await updatedCard.getByRole("button", { name: "Delete" }).click();
    await expect(page.locator(".todoCard", { hasText: "Prepare board memo v2" })).toHaveCount(0);
  });

  test("records a focus session through the planner service", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Start 25 min focus" }).first().click();
    await expect(page.getByText("Sessions captured by the planner service.")).toBeVisible();
    await expect(page.locator(".sessionCard")).toHaveCount(1);
  });
});
