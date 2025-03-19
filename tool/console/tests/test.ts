import { expect, test, type Locator, type Page } from '@playwright/test';
import { schema } from './constants';

async function selectAllCopyAndGet(page: Page, locator: Locator): Promise<string> {
	await locator.click();

	if (process.platform === 'darwin') {
		await page.keyboard.press('Meta+A');
		await page.keyboard.press('Meta+C');
	} else {
		await page.keyboard.press('Control+A');
		await page.keyboard.press('Control+C');
	}

	await page.keyboard.press('Escape');

	return await page.evaluate(() => navigator.clipboard.readText());
}

test.describe('Loading from demo server', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		await expect(
			page.getByRole('heading', { name: 'MsgPact' }),
			"Page should have a heading with the text 'MsgPact'"
		).toBeVisible();
		
		let source = page.getByRole('textbox', { name: 'Source' });
		await source.fill('http://localhost:8080/api');
		await page.getByRole('button', { name: 'Load'}).click();
	});

	test('Schema editor works correctly', async ({ page }) => {
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

		expect(
			await selectAllCopyAndGet(page, textAreaElement.locator("..")),
			"Clipboard should contain the schema text"
		).toBe(schema);
	
		await textAreaElement.locator("..").click();
		await page.keyboard.press('a');
	
		expect(
			await selectAllCopyAndGet(page, textAreaElement.locator("..")),
			"Editor should not have changed since it is not editable"
		).toBe(schema);
	});

	test('Doc UI shows examples correctly', async ({ page }) => {
	
		let infoCard = page.getByRole('region', { name: 'info.DevConsole'});
		await expect(
			infoCard,
			"DevConsole info should be visible"
		).toBeVisible();
	
		let fnCard = page.getByRole('region', { name: 'fn.fn1'});
		await expect(
			fnCard,
			"fn1 function should be visible"
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
			"Example button should toggle after clicking"
		).toBeVisible();
	
		await expect(
			fnArguments.getByRole('button', { name: 'Regenerate'}),
			"Regenerate button should be visible after example is shown"
		).toBeVisible();
	
		let fnArgumentsExample = fnArguments.getByRole('textbox', { name: 'fn.fn1.example'});
		await expect(
			fnArgumentsExample,
			"Example text area should be visible after clicking the button"
		).toBeVisible();
	
		let fnArgExampleText = await selectAllCopyAndGet(page, fnArgumentsExample.locator(".."));
	
		let fnArgExamplePsuedoJson = JSON.parse(fnArgExampleText);
	
		expect(
			fnArgExamplePsuedoJson,
			"Example text should be valid JSON"
		).toMatchObject({
			"fn.fn1": {
			}
		});
	
		if ("limit!" in fnArgExamplePsuedoJson["fn.fn1"]) {
			expect(
				typeof fnArgExamplePsuedoJson["fn.fn1"]["limit!"],
				"Generated example should have correct types"
			).toBe('number');
		}

		let fnResult = fnCard.getByRole('region', { name: 'Result'});
		await expect(
			fnResult,
			"Result section should be visible"
		).toBeVisible();

		await expect(
			fnResult.getByRole('button', { name: 'Regenerate'}),
			"Regenerate button should be hidden before example is shown"
		).toBeHidden();
		
		await fnResult.getByRole('button', { name: 'Example'}).click();

		await expect(
			fnResult.getByRole('button', { name: 'Example', exact: true }),
			"Example button should toggle after clicking"
		).toBeHidden();

		await expect(
			fnResult.getByRole('button', { name: 'Hide Example'}),
			"Example button should toggle after clicking"
		).toBeVisible();

		await expect(
			fnResult.getByRole('button', { name: 'Regenerate'}),
			"Regenerate button should be visible after example is shown"
		).toBeVisible();

		let fnResultExample = fnResult.getByRole('textbox', { name: 'fn.fn1.result.example'});
		await expect(
			fnResultExample,
			"Example text area should be visible after clicking the button"
		).toBeVisible();

		let fnResultExampleText = await selectAllCopyAndGet(page, fnResultExample.locator(".."));

		let fnResultExamplePsuedoJson = JSON.parse(fnResultExampleText);

		expect(
			fnResultExamplePsuedoJson,
			"Example text should be valid JSON"
		).toMatchObject({
			"Ok_": {
				"output1": [
					{
						"field1": expect.any(String),
						"field2": expect.any(Number)
					},
					{
						"field1": expect.any(String),
						"field2": expect.any(Number)
					}
				]
			}
		});
		
	});

	test('Doc UI follows links correctly', async ({ page }) => {
			
		let fnCard = page.getByRole('region', { name: 'fn.fn1'});
		await expect(
			fnCard,
			"fn1 function should be visible"
		).toBeVisible();

		await expect(
			page.getByRole('region', { name: 'struct.Struct1'}),
			"Struct1 struct should not yet be visible"
		).not.toBeInViewport();

		await fnCard.getByRole('link', { name: 'Struct1'}).first().click();

		await expect(
			page.getByRole('region', { name: 'struct.Struct1'}),
			"Struct1 struct should be visible"
		).toBeInViewport();
	
	});
	
});

