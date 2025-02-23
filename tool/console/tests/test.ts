import { expect, test } from '@playwright/test';

test('index page has expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'uAPI' })).toBeVisible();
	let source = page.getByRole('textbox', { name: 'Source' });
	await source.fill('http://localhost:8000/api');
	await page.getByRole('button', { name: 'Load' }).click();
	await expect(page.getByRole('heading', { name: 'info.Calculator' })).toBeVisible();
});
