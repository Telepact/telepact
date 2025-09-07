//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

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

async function ctrlClick(page: Page, locator: Locator) {
	if (process.platform === 'darwin') {
		await page.keyboard.down('Meta');
	} else {
		await page.keyboard.down('Control');
	}
	await locator.click();
	await page.keyboard.up('Meta');
	await page.keyboard.up('Control');
}

test.describe('Loading from demo server', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		await expect(
			page.getByRole('heading', { name: 'Telepact' }),
			"Page should have a heading with the text 'Telepact'"
		).toBeVisible();
		
		let source = page.getByRole('textbox', { name: 'Source' });
		await source.fill('http://localhost:8085/api');
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

		await expect(page.getByRole('heading', {name: 'Schema'})).toBeVisible();
	
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

	test('Doc UI shows internal API correctly', async ({ page }) => {
		let fnCard = page.getByRole('region', { name: 'fn.ping_'});
		await expect(
			fnCard,
			"ping_ function should not be visible"
		).not.toBeVisible();

		await page.getByRole('button', { name: 'Show Internal API'} ).click();

		await expect(
			fnCard,
			"ping_ function should be visible"
		).toBeVisible();
	});	

	test('Doc UI correctly navigates to simulation', async ({ page }) => {
	
		let fnCard = page.getByRole('region', { name: 'fn.fn1'});
		await expect(
			fnCard,
			"fn1 function should be visible"
		).toBeVisible();

		await expect(page.getByRole('button', { name: 'Toggle Simulation', pressed: false })).toBeVisible();

		await fnCard.getByRole('button', { name: 'Simulate'}).click();

		await expect(
			page.getByRole('button', { name: 'Toggle Simulation', pressed: true }),
			"Schema should be visible after navigating to simulation"
		).toBeVisible();

		let requestSimulation = page.getByRole('textbox', { name: 'requestExample'});
		await expect(
			requestSimulation,
			"Request simulation should be visible"
		).toBeVisible();
	
		let requestSimulationText = await selectAllCopyAndGet(page, requestSimulation.locator(".."));
	
		let requestSimulationPseudoJson = JSON.parse(requestSimulationText);
	
		expect(
			requestSimulationPseudoJson,
			"Request simluation should be valid json"
		).toMatchObject([{
		}, {
			"fn.fn1": {
				"input1": expect.any(String),
				"input2": expect.any(Number)
			}
		}]);
		
		let responseSimulation = page.getByRole('textbox', { name: 'responseExample'});
		await expect(
			responseSimulation,
			"Response simluation should be visible"
		).toBeVisible();
	
		let responseSimulationText = await selectAllCopyAndGet(page, responseSimulation.locator(".."));
	
		let responseSimulationPseudoJson = JSON.parse(responseSimulationText);
	
		expect(
			responseSimulationPseudoJson,
			"Response simulation should be valid json"
		).toMatchObject([{}, {
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
		}]);			
		
	});

	test('Terminal functions corectly', async ({ page }) => {

		await expect(page.getByRole('heading', {name: 'Request'})).not.toBeVisible();

		await page.getByRole('button', { name: 'Toggle Terminal', pressed: false}).click();

		await expect(page.getByRole('heading', {name: 'Request'})).toBeVisible();

		await expect(
			page.getByRole('button', { name: 'Toggle Terminal', pressed: true }),
			"Terminal should be visible after clicking the button"
		).toBeVisible();

		let request = page.getByRole('textbox', { name: 'request'});
		await expect(
			request,
			"Request simulation should be visible"
		).toBeVisible();
	
		let requestText = await selectAllCopyAndGet(page, request.locator(".."));
	
		let requestPseudoJson = JSON.parse(requestText);
	
		expect(
			requestPseudoJson,
			"Request simluation should be valid json"
		).toEqual([{
		}, {
			"fn.ping_": {
			}
		}]);

		await expect(page.getByRole('heading', { name: 'Response'})).not.toBeVisible();

		await expect(page.getByRole('button', {name: 'Toggle Results', pressed: false})).toBeVisible();

		let promptCount = 0;
		page.on('dialog', async dialog => {
			promptCount += 1;
			await dialog.accept();
		});
		
		await page.getByRole('button', { name: 'Submit (live)'}).click();

		await expect(page.getByRole('heading', { name: 'Response'})).toBeVisible();

		await expect(page.getByRole('button', {name: 'Toggle Results', pressed: true})).toBeVisible();

		let response = page.getByRole('textbox', { name: 'response'});
		await expect(
			response,
			"response should be visible"
		).toBeVisible();
	
		let responseText = await selectAllCopyAndGet(page, response.locator(".."));
	
		let responsePseudoJson = JSON.parse(responseText);
	
		expect(
			responsePseudoJson,
			"response should be valid json"
		).toEqual([{
		}, {
			"Ok_": {
			}
		}]);
		
		await request.locator('..').click();

		if (process.platform === 'darwin') {
			await page.keyboard.press('Meta+A');
		} else {
			await page.keyboard.press('Control+A');
		}

		await page.keyboard.press('Backspace');

		await page.keyboard.type('[{}, {"fn.fnA": {}}]');

		await page.getByRole('button', { name: 'Submit (live)'}).click();

		let response2 = page.getByRole('textbox', { name: 'response'});
	
		let response2Text = await selectAllCopyAndGet(page, response2.locator(".."));
	
		let response2PseudoJson = JSON.parse(response2Text);

		console.log(JSON.stringify(response2PseudoJson));
	
		expect(
			response2PseudoJson,
			"response should be valid json"
		).toMatchObject([{}, {
			"Ok_": {
				"linkA": {
					"fn.fn1": {
						"input1": expect.any(String),
						"input2": expect.any(Number)
					}
				}
			}
		}]);

		let linkLocator = page.getByText('fn.fn1');

		await expect(
			linkLocator,
			"fn.fn1 link should be visible"
		).toBeVisible();

		await ctrlClick(page, linkLocator);

		await expect(page.getByRole('textbox', { name: 'response'})).not.toBeVisible();

		let request2 = page.getByRole('textbox', { name: 'request'});
		let request2Text = await selectAllCopyAndGet(page, request2.locator(".."));
		let request2PseudoJson = JSON.parse(request2Text);
		expect(
			request2PseudoJson,
			"request should be valid json"
		).toEqual([{}, {
			"fn.fn1": {
				"input1": expect.any(String),
				"input2": expect.any(Number)
			}
		}]);

		await page.getByRole('button', { name: 'Submit (live)'}).click();

		let response3 = page.getByRole('textbox', { name: 'response'});
	
		let response3Text = await selectAllCopyAndGet(page, response3.locator(".."));
	
		let response3PseudoJson = JSON.parse(response3Text);

		console.log(JSON.stringify(response3PseudoJson));
	
		expect(
			response3PseudoJson,
			"response should be valid json"
		).toMatchObject([{}, {
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
		}]);

		expect(promptCount).toBe(1);
	});
	
});

