import { expect, test, type Page } from '@playwright/test';
import { text } from 'stream/consumers';
import { demoSchema } from './constants';

test('Console is working correctly', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'msgPact' })).toBeVisible();
	let source = page.getByRole('textbox', { name: 'Source' });
	await source.fill('http://localhost:8000/api');
	
	await page.getByRole('button', { name: 'Load'}).click();

	await expect(page.getByRole('button', { name: 'Toggle Documentation', pressed: true })).toBeVisible();
	await expect(page.getByRole('heading', { name: 'info.Calculator' })).toBeVisible();

	await page.getByRole('button', { name: 'Toggle Schema', pressed: false }).click();
	await expect(page.getByRole('button', { name: 'Toggle Schema', pressed: true })).toBeVisible();
	
	let textAreaElement = page.getByRole('textbox', { name: 'schema'});
	await expect(textAreaElement).toBeVisible();

	await textAreaElement.locator("..").click();

	if (process.platform === 'darwin') {
		await page.keyboard.press('Meta+A');
		await page.keyboard.press('Meta+C');
	} else {
		await page.keyboard.press('Control+A');
		await page.keyboard.press('Control+C');
	}

	expect(await getClipboardText(page)).toBe(demoSchema);

	await textAreaElement.locator("..").click();
	await page.keyboard.press('a');

	// Editor should not have changed, since it is not editable
	expect(await getClipboardText(page)).toBe(demoSchema);
});

async function getClipboardText(page: Page): Promise<string> {
	if (process.platform === 'darwin') {
		await page.keyboard.press('Meta+A');
		await page.keyboard.press('Meta+C');
	} else {
		await page.keyboard.press('Control+A');
		await page.keyboard.press('Control+C');
	}

	return await page.evaluate(() => navigator.clipboard.readText());
}

