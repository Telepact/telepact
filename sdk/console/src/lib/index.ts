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

// place files you want to import through the `$lib` alias in this folder.
import { goto } from '$app/navigation';
import * as monaco from 'monaco-editor';
import * as telepact from './telepact/index.esm.js';
import { _internal } from './telepact/index.esm.js';
import { writable, type Writable } from 'svelte/store';
import { createJsonSchema } from './jsonSchema';

export function createJsonSchema2(telepact: telepact.TelepactSchema): Record<string, any> {
	return createJsonSchema(telepact);
}

export const responseStore: Writable<string | null> = writable(null);
const authHeaderStore: Writable<Record<string, any> | null> = writable(null);

export const stockPingRequest = `[
  {},
  {
    "fn.ping_": {}
  }
]
`;

export const stockPingResponse = `[
  {},
  {
    "Ok_": {}
  }
]
`;

const random = new telepact.RandomGenerator(2, 2);

export function minifyJson(json: string, redactAuthHeader = false) {
	let pseudoJson = JSON.parse(json);

	if (redactAuthHeader) {
		let authHeader = pseudoJson[0]['@auth_'];

		if (authHeader !== undefined) {
			pseudoJson[0]['@auth_'] = '{{redacted}}';
			authHeaderStore.set(authHeader);
		}
	}

	return JSON.stringify(pseudoJson);
}

export function unMinifyJson(json: string | null, authManaged: boolean = false) {
	if (!json) {
		return stockPingRequest;
	}
	let pseudoJson = JSON.parse(json);

	if (authManaged) {
		pseudoJson[0]['@auth_'] = '{{managed}}';
	}

	let authHeader = pseudoJson[0]['@auth_'];
	if (authHeader === '{{redacted}}') {
		authHeaderStore.subscribe((authHeader) => {
			if (authHeader !== null) {
				pseudoJson[0]['@auth_'] = authHeader;
			}
		})();
		authHeaderStore.set(null);
	}

	return JSON.stringify(pseudoJson, null, 2);
}

export function handleRequest(request: string, viewQuery: string) {
	let minifiedRequest = minifyJson(request, true);
	let q = new URLSearchParams(window.location.search);
	if (viewQuery !== undefined) {
		q.set('v', viewQuery);
	}
	q.set('r', minifiedRequest);
	goto(`?${q.toString()}`);
}

export function handleSubmitRequest(client: telepact.Client, request: string) {
	let requestPseudoJson = JSON.parse(request);
	let requestMessage = new telepact.Message(requestPseudoJson[0], requestPseudoJson[1]);
	client
		.request(requestMessage)
		.then((rs: telepact.Message) => JSON.stringify([rs.headers, rs.body], null, 2))
		.then((res) => {
			responseStore.set(res);
		});
}

function lastChar(str: string) {
	return str[str.length - 1] ?? '';
}

export interface UnionTagTypeData {
	name: string;
	doc: string | string[];
	data: Record<string, any>;
}

export interface FnTypeData {
	args: Record<string, any>;
	results: UnionTagTypeData[];
	errorRegex: string;
	inheritedErrors: string[];
	exampleCallJson: string;
}

export interface TypeData {
	name: string;
	doc: string | string[];
	data: FnTypeData | Record<string, any> | UnionTagTypeData[];
}

export interface HeaderData {
	type: 'header';
	name: string;
	doc: string | string[];
	requestData: Record<string, any>;
	responseData: Record<string, any>;
}

export function isFnTypeData(data: any): data is FnTypeData {
	return (data as FnTypeData).args !== undefined && (data as FnTypeData).results !== undefined;
}

export function isUnionTagTypeData(data: any): data is UnionTagTypeData[] {
	return (
		Array.isArray(data) &&
		data.length > 0 &&
		(data[0] as UnionTagTypeData).name !== undefined &&
		(data[0] as UnionTagTypeData).data !== undefined
	);
}

export function isHeaderData(data: any): data is HeaderData {
	return (data as HeaderData).type === 'header';
}

export function generateExample(schemaKey: string, schemaInst: telepact.TelepactSchema) {
	let example = schemaInst.parsed[schemaKey].generateRandomValue(
		null,
		false,
		[],
		new _internal.GenerateContext(true, true, true, '', random)
	);
	return JSON.stringify(example, null, 2);
}

export function generateFnResultExample(
	fn: string,
	schemaInst: telepact.TelepactSchema,
	blueprintValue: any,
	useBlueprintValue: boolean
) {
	let exampleResult = schemaInst.parsed[fn].result.generateRandomValue(
		blueprintValue,
		useBlueprintValue,
		[],
		new _internal.GenerateContext(true, true, true, fn, random)
	);
	return JSON.stringify(exampleResult, null, 2);
}

export function generateHeaderExample(
	headerType: 'request' | 'response',
	headers: string[],
	schemaInst: telepact.TelepactSchema
) {
	console.log(`schemaInst.parsedRequestHeaders ${Object.keys(schemaInst.parsedRequestHeaders)}`);
	let genHeaders: Record<string, any> = {};
	for (const header of headers) {
		if (headerType == 'request') {
			const genHeader = schemaInst.parsedRequestHeaders[
				header
			]?.typeDeclaration?.generateRandomValue(
				null,
				false,
				new _internal.GenerateContext(true, true, true, 'fn.ping_', random)
			);
			genHeaders[header] = genHeader;
		} else {
			const genHeader = schemaInst.parsedResponseHeaders[
				header
			]?.typeDeclaration?.generateRandomValue(
				null,
				false,
				new _internal.GenerateContext(true, true, true, 'fn.ping_', random)
			);
			genHeaders[header] = genHeader;
		}
	}

	return JSON.stringify(genHeaders, null, 2);
}

export async function genExample(
	fn: string,
	headers: Array<string>,
	schemaInst: telepact.TelepactSchema
) {
	console.log(`Generating example for ${fn} with headers ${headers}`);
	let example = schemaInst.parsed[fn].generateRandomValue(
		null,
		false,
		[],
		new _internal.GenerateContext(true, true, true, fn, random)
	);
	let requestHeaders: Record<string, any> = {};
	for (const header of headers) {
		requestHeaders[header] = schemaInst.parsedRequestHeaders[
			header
		]?.typeDeclaration?.generateRandomValue(
			null,
			false,
			new _internal.GenerateContext(true, true, true, fn, random)
		);
	}
	let request = [requestHeaders, example];
	let requestJson = JSON.stringify(request, null, 2);
	let requestBytes = new TextEncoder().encode(requestJson);
	let mockServerOptions = new telepact.MockServerOptions();
	let mockTelepact = new telepact.MockTelepactSchema(
		schemaInst.original,
		schemaInst.full,
		schemaInst.parsed,
		schemaInst.parsedRequestHeaders,
		schemaInst.parsedResponseHeaders
	);
	let mockServer = new telepact.MockServer(mockTelepact, mockServerOptions);
	let responseBytes = await mockServer.process(requestBytes);
	try {
		let responseJson = new TextDecoder().decode(responseBytes);
		let response = JSON.parse(responseJson);
		let finalResponseJson = JSON.stringify(response, null, 2);
		return {
			request: requestJson,
			response: finalResponseJson
		};
	} catch (error) {
		// Convert responseBytes to a hex string
		let hexResponse = Array.from(responseBytes)
			.map((byte, index) => {
				const char =
					byte >= 32 && byte <= 126
						? String.fromCharCode(byte)
						: '0x' + byte.toString(16).padStart(2, '0');
				const newline = (index + 1) % 16 === 0 ? '\n' : '';
				return char;
			})
			.join('');
		return {
			request: requestJson,
			response: hexResponse
		};
	}
}

export function parseTelepactSchema(
	schema: any[],
	schemaInst: telepact.TelepactSchema,
	sortDocCardsAZ: boolean,
	showInternalApi: boolean
): TypeData[] {
	console.log(`Parsing schema with ${schemaInst} ${schemaInst.full} ${schemaInst.original}`);
	let pseudoJson: Record<string, any>[] = showInternalApi ? schemaInst.full : schemaInst.original;

	let preppedPseudoJson = pseudoJson.map((e) => [findSchemaKey(e), e] as [string, any]);

	let availableErrors = preppedPseudoJson
		.filter(([schemaKey, e2]) => {
			return schemaKey.startsWith('errors');
		})
		.map(([schemaKey, e2]) => {
			let doc = e2['///'];
			return {
				name: schemaKey,
				doc: doc,
				data: e2[schemaKey]
			} as UnionTagTypeData;
		});

	let results: TypeData[] = preppedPseudoJson.map(([schemaKey, e]) => {
		let data: any;
		if (schemaKey.startsWith('union')) {
			data = e[schemaKey].map((e2: any) => {
				let enumTag = Object.keys(e2).find((k) => k !== '///') as string;
				let doc = e2['///'];
				return {
					name: enumTag,
					doc: doc,
					data: e2[enumTag]
				} as UnionTagTypeData;
			});
		} else if (schemaKey.startsWith('error')) {
			data = e[schemaKey].map((e2: any) => {
				let enumTag = Object.keys(e2).find((k) => k !== '///') as string;
				let doc = e2['///'];
				return {
					name: enumTag,
					doc: doc,
					data: e2[enumTag]
				} as UnionTagTypeData;
			});
		} else if (schemaKey.startsWith('fn')) {
			let argData = e[schemaKey];
			let resultData = e['->'].map((e2: any) => {
				let enumTag = Object.keys(e2).find((k) => k !== '///') as string;
				let doc = e2['///'];
				return {
					name: enumTag,
					doc: doc,
					data: e2[enumTag]
				} as UnionTagTypeData;
			});

			let exampleCall = schemaInst.parsed[schemaKey].generateRandomValue(
				null,
				false,
				[],
				new _internal.GenerateContext(
					true,
					false,
					true,
					schemaKey,
					new telepact.RandomGenerator(2, 2)
				)
			);
			let exampleCallJson = JSON.stringify([{}, exampleCall]);

			let errorsRegex = e['_errors'];
			let inheritedErrors = availableErrors
				.filter((e4) => {
					return e4.name.match(errorsRegex);
				})
				.map((e4) => e4.name);

			data = {
				args: argData,
				results: resultData,
				errorRegex: errorsRegex,
				exampleCallJson: exampleCallJson,
				inheritedErrors: inheritedErrors
			};
		} else if (schemaKey.startsWith('headers')) {
			let doc = e['///'];
			let requestData = e[schemaKey];
			let responseData = e['->'];
			data = {
				type: 'header',
				name: schemaKey,
				doc: doc,
				requestData: requestData,
				responseData: responseData
			} as HeaderData;
		} else {
			data = e[schemaKey];
		}

		return {
			name: schemaKey,
			doc: e['///'],
			data: data
		} as TypeData;
	});

	if (sortDocCardsAZ) {
		results.sort((e1, e2) => {
			let tokens1 = Object.keys(e1)[0].split('.');
			let tokens2 = Object.keys(e2)[0].split('.');
			let key1 = tokens1[1] ?? '';
			let key2 = tokens2[1] ?? '';
			let result = 0;
			if (lastChar(key1) === '_' || lastChar(key2) === '_') {
				result = lastChar(key2).localeCompare(lastChar(key1));
			}
			if (result === 0) {
				if (tokens1[0] === 'fn' && tokens2[0] !== 'fn') {
					result = -1;
				} else if (tokens1[0] !== 'fn' && tokens2[0] === 'fn') {
					result = 1;
				}
			}
			if (result === 0) {
				result = key1.localeCompare(key2);
			}
			return result;
		});
	}

	return results;
}

export function findSchemaKey(definition: Record<string, any>): string {
	const regex = '^(((fn|errors|info|headers)|((struct|union|_ext)(<[0-2]>)?))\\..*)';
	const matches: string[] = [];

	for (const e of Object.keys(definition)) {
		if (e.match(regex)) {
			matches.push(e);
		}
	}

	const result = matches[0];

	if (matches.length === 1 && result != undefined) {
		return result;
	} else {
		throw Error(`Could not find schema key ${JSON.stringify(definition)} with regex ${regex}`);
	}
}

monaco.languages.typescript.typescriptDefaults.setEagerModelSync(true);
// monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
// 	schemas: [
// 		{
// 			uri: 'internal://server/jsonschema.json',
// 			fileMatch: ['schema.telepact.json'],
// 			schema: telepact.jsonSchema
// 		}
// 	]
// });
monaco.languages.registerLinkProvider('json', {
	provideLinks: (
		model: monaco.editor.ITextModel,
		token: monaco.CancellationToken
	): monaco.languages.ProviderResult<monaco.languages.ILinksList> => {
		let matches = model.findMatches(
			'\\{[\\s\\n]*"fn\\..*":[\\s\\n]*\\{',
			false,
			true,
			false,
			'',
			false,
			undefined
		);

		let links: { range: monaco.Range }[] = matches
			.map((m) => {
				// @ts-ignore
				let end: [monaco.Range, monaco.Range] = model._bracketPairs.matchBracket(
					new monaco.Position(m.range.startLineNumber, m.range.startColumn)
				);

				if (!end) {
					return null;
				}

				let ran = new monaco.Range(
					m.range.startLineNumber,
					m.range.startColumn,
					end[1].endLineNumber,
					end[1].endColumn
				);

				let str = model.getValueInRange(ran);

				return { range: ran, val: str };
			})
			.filter((e) => e !== null) as { range: monaco.Range }[];
		return {
			links: links
		};
	},
	resolveLink: (
		link: monaco.languages.ILink,
		token: monaco.CancellationToken
	): monaco.languages.ProviderResult<monaco.languages.ILink> => {
		// @ts-ignore
		handleRequest(JSON.stringify([{}, JSON.parse(link.val)]));

		responseStore.set(null);

		return {
			range: link.range
		};
	}
});
monaco.languages.registerLinkProvider('json', {
	provideLinks: (
		model: monaco.editor.ITextModel,
		token: monaco.CancellationToken
	): monaco.languages.ProviderResult<monaco.languages.ILinksList> => {
		return {
			links: []
		};
	},
	resolveLink: (
		link: monaco.languages.ILink,
		token: monaco.CancellationToken
	): monaco.languages.ProviderResult<monaco.languages.ILink> => {
		return {
			range: link.range
		};
	}
});

// TODO: Consider if a source map would help links
function generateJsonSourceMap(jsonString: string): any[] {
	const sourceMap: any[] = [];
	let path: (string | number)[] = [];
	let line = 1;
	let column = 1;

	let inString = false;
	let currentKey = '';
	let currentArrayIndex = -1; // Tracks the current array index
	let keyStartColumn = 0;

	// Helper function to add to source map
	const addToSourceMap = (
		key: string | number,
		keyLine: number,
		keyColumnStart: number,
		keyColumnEnd: number
	) => {
		sourceMap.push({
			path: [...path, key],
			line: keyLine,
			columnStart: keyColumnStart,
			columnEnd: keyColumnEnd
		});
	};

	for (let i = 0; i < jsonString.length; i++) {
		const char = jsonString[i];

		// Handle line and column tracking
		if (char === '\n') {
			line++;
			column = 0;
		} else {
			column++;
		}

		// Toggle inString state
		if (char === '"' && jsonString[i - 1] !== '\\') {
			inString = !inString;
			if (inString) {
				keyStartColumn = column;
			} else {
				// End of string, add key to source map if we're not in an array
				if (path.length > 0 && typeof path[path.length - 1] !== 'number') {
					addToSourceMap(currentKey, line, keyStartColumn, column);
				}
				currentKey = '';
			}
			continue;
		}

		// Collect characters of a key
		if (inString) {
			currentKey += char;
		}

		// Handle object and array parsing
		if (!inString) {
			if (char === '{' || char === '[') {
				// Entering a new object or array
				if (currentKey) {
					path.push(currentKey);
					currentKey = '';
					if (char === '[') {
						currentArrayIndex = 0; // Initialize array index
					}
				} else if (char === '[') {
					if (currentArrayIndex === -1) {
						currentArrayIndex = 0; // Initialize array index at the start of a new array
					} else {
						path.push(currentArrayIndex);
						currentArrayIndex = 0; // Reset for new nested array
					}
				}
			} else if (char === '}' || char === ']') {
				// Exiting an object or array
				if (char === ']') {
					if (typeof path[path.length - 1] === 'number') {
						path.pop(); // Remove the array index when exiting the array
					}
					let lastIndex = path.length - 1;
					currentArrayIndex =
						path.length > 0 && typeof lastIndex === 'number' ? lastIndex + 1 : -1;
				} else {
					currentArrayIndex = -1; // Reset array index when exiting an object
				}
				if (currentKey) {
					path.pop();
					currentKey = '';
				}
			} else if (char === ',' && typeof path[path.length - 1] === 'number') {
				// Next item in array
				currentArrayIndex++;
				path[path.length - 1] = currentArrayIndex;
			}
		}
	}

	return sourceMap;
}
