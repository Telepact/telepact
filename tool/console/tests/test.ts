import { expect, test } from '@playwright/test';
import { text } from 'stream/consumers';

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

	const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
	expect(clipboardText).toBe(
`[
  {
    "///": " A calculator app that provides basic math computation capabilities. ",
    "info.Calculator": {}
  },
  {
    "///": " Compute the \`result\` of the given \`x\` and \`y\` values. ",
    "fn.compute": {
      "x": ["union.Value"],
      "y": ["union.Value"],
      "op": ["union.Operation"]
    },
    "->": [
      {
        "Ok_": {
          "result": ["number"]
        }
      },
      {
        "ErrorCannotDivideByZero": {}
      }
    ]
  },
  {
    "///": " Export all saved variables, up to an optional \`limit\`. ",
    "fn.exportVariables": {
      "limit!": ["integer"]
    },
    "->": [
      {
        "Ok_": {
          "variables": ["array", ["struct.Variable"]]
        }
      }
    ]
  },
  {
    "///": " A function template. ",
    "fn.getPaperTape": {},
    "->": [
      {
        "Ok_": {
          "tape": ["array", ["struct.Computation"]]
        }
      }
    ]
  },
  {
    "///": " Save a set of variables as a dynamic map of variable names to their value. ",
    "fn.saveVariables": {
      "variables": ["object", ["number"]]
    },
    "->": [
      {
        "Ok_": {}
      }
    ]
  },
  {
    "fn.showExample": {},
    "->": [
      {
        "Ok_": {
          "link": ["fn.compute"]
        }
      }
    ]
  },
  {
    "///": " A computation. ",
    "struct.Computation": {
      "firstOperand": ["union.Value"],
      "secondOperand": ["union.Value"],
      "operation": ["union.Operation"],
      "timestamp": ["integer"],
      "successful": ["boolean"]
    }
  },
  {
    "///": " A mathematical variable represented by a \`name\` that holds a certain \`value\`. ",
    "struct.Variable": {
      "name": ["string"],
      "value": ["number"]
    }
  },
  {
    "///": " A basic mathematical operation. ",
    "union.Operation": [
      {
        "Add": {}
      },
      {
        "Sub": {}
      },
      {
        "Mul": {}
      },
      {
        "Div": {}
      }
    ]
  },
  {
    "///": " A value for computation that can take either a constant or variable form. ",
    "union.Value": [
      {
        "Constant": {
          "value": ["number"]
        }
      },
      {
        "Variable": {
          "name": ["string"]
        }
      }
    ]
  }
]`);
});

