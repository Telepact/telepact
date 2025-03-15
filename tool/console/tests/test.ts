import { expect, test, type Page } from '@playwright/test';
import { demoSchema } from './constants';

async function selectAllCopyAndGet(page: Page): Promise<string> {
	if (process.platform === 'darwin') {
		await page.keyboard.press('Meta+A');
		await page.keyboard.press('Meta+C');
	} else {
		await page.keyboard.press('Control+A');
		await page.keyboard.press('Control+C');
	}

	return await page.evaluate(() => navigator.clipboard.readText());
}

test('Console works correctly', async ({ page }) => {
	await page.goto('/');
	await expect(
		page.getByRole('heading', { name: 'MsgPact' }),
		"Page should have a heading with the text 'MsgPact'"
	).toBeVisible();
	
	let source = page.getByRole('textbox', { name: 'Source' });
	await source.fill('http://localhost:8000/api');
	
	await page.getByRole('button', { name: 'Load'}).click();

	await expect(
		page.getByRole('button', { name: 'Toggle Documentation', pressed: true }),
		"Documentation should be visible by default"
	).toBeVisible();
	
	await page.getByRole('button', { name: 'Toggle Schema', pressed: false }).click();
	await expect(
		page.getByRole('button', { name: 'Toggle Schema', pressed: true }),
		"Schema should be visible after clicking the button"
	).toBeVisible();
	
	let textAreaElement = page.getByRole('textbox', { name: 'schema'});
	await expect(
		textAreaElement,
		"Schema text area should be visible after clicking the button"
	).toBeVisible();

	await textAreaElement.locator("..").click();

	expect(
		await selectAllCopyAndGet(page),
		"Clipboard should contain the schema text"
	).toBe(demoSchema);

	await textAreaElement.locator("..").click();
	await page.keyboard.press('a');

	expect(
		await selectAllCopyAndGet(page),
		"Editor should not have changed since it is not editable"
	).toBe(demoSchema);

	let infoCard = page.getByRole('region', { name: 'info.Calculator'});
	await expect(
		infoCard,
		"Calculator info should be visible"
	).toBeVisible();

	let fnCard = page.getByRole('region', { name: 'fn.exportVariables'});
	await expect(
		fnCard,
		"exportVariables function should be visible"
	).toBeVisible();

	let fnArguments = fnCard.getByRole('region', { name: 'Arguments'});
	await expect(
		fnArguments,
		"Arguments section should be visible"
	).toBeVisible();

	await expect(
		fnArguments.getByRole('button', { name: 'Regenerate'}),
		"Regenerate button should be hidden before example is shown"
	).toBeHidden();

	await fnArguments.getByRole('button', { name: 'Example'}).click();

	await expect(
		fnArguments.getByRole('button', { name: 'Example', exact: true }),
		"Example button should toggle after clicking"
	).toBeHidden();

	await expect(
		fnArguments.getByRole('button', { name: 'Hide Example'}),
		"Example button should toggel after clicking"
	).toBeVisible();

	await expect(
		fnArguments.getByRole('button', { name: 'Regenerate'}),
		"Regenerate button should be visible after example is shown"
	).toBeVisible();

	let fnArgumentsExample = fnArguments.getByRole('textbox', { name: 'fn.exportVariables.example'});
	await expect(
		fnArgumentsExample,
		"Example text area should be visible after clicking the button"
	).toBeVisible();

	await fnArgumentsExample.locator("..").click();

	let fnArgExampleText = await selectAllCopyAndGet(page);

	let fnArgExamplePsuedoJson = JSON.parse(fnArgExampleText);

	expect(
		fnArgExamplePsuedoJson,
		"Example text should be valid JSON"
	).toMatchObject({
		"fn.exportVariables": {}
	});

	if ("limit!" in fnArgExamplePsuedoJson["fn.exportVariables"]) {
		expect(
			typeof fnArgExamplePsuedoJson["fn.exportVariables"]["limit!"],
			"Generated example should have correct types"
		).toBe('number');
	}

});
