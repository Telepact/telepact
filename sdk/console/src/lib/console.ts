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

import { parse } from 'marked';
import DOMPurify from 'dompurify';
import { parseDocument } from 'yaml';

import * as telepact from './telepact/index.esm.js';
import { _internal } from './telepact/index.esm.js';

const random = new telepact.RandomGenerator(2, 2);

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

let redactedAuthHeader: Record<string, any> | null = null;

export function minifyJson(json: string, redactAuthHeader = false) {
	const pseudoJson = JSON.parse(json);

	if (redactAuthHeader) {
		const authHeader = pseudoJson?.[0]?.['+auth_'];
		if (authHeader !== undefined) {
			pseudoJson[0]['+auth_'] = '{{redacted}}';
			redactedAuthHeader = authHeader;
		}
	}

	return JSON.stringify(pseudoJson);
}

export function minifySchemaDraft(schemaDraft: string) {
	const document = parseDocument(schemaDraft);

	if (document.errors.length > 0) {
		throw document.errors[0];
	}

	return JSON.stringify(document.toJS());
}

export function unMinifyJson(json: string | null, authManaged = false) {
	if (!json) {
		return stockPingRequest;
	}

	const pseudoJson = JSON.parse(json);

	if (authManaged) {
		pseudoJson[0]['+auth_'] = '{{managed}}';
	}

	if (pseudoJson?.[0]?.['+auth_'] === '{{redacted}}' && redactedAuthHeader !== null) {
		pseudoJson[0]['+auth_'] = redactedAuthHeader;
		redactedAuthHeader = null;
	}

	return JSON.stringify(pseudoJson, null, 2);
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

export function markdownHtml(entry: Record<string, any>): string {
	const descriptionDef = entry.doc;
	const descriptionStr = Array.isArray(descriptionDef)
		? descriptionDef.map((l) => l.trim()).join('\n')
		: descriptionDef;
	const html = typeof descriptionStr === 'string' ? (parse(descriptionStr) as string) : '';
	return DOMPurify.sanitize(html);
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
	const example = schemaInst.parsed[schemaKey].generateRandomValue(
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
	const exampleResult = schemaInst.parsed[fn + '.->'].generateRandomValue(
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
	const genHeaders: Record<string, any> = {};
	for (const header of headers) {
		if (headerType === 'request') {
			genHeaders[header] = schemaInst.parsedRequestHeaders[header]?.typeDeclaration?.generateRandomValue(
				null,
				false,
				new _internal.GenerateContext(true, true, true, 'fn.ping_', random)
			);
		} else {
			genHeaders[header] = schemaInst.parsedResponseHeaders[header]?.typeDeclaration?.generateRandomValue(
				null,
				false,
				new _internal.GenerateContext(true, true, true, 'fn.ping_', random)
			);
		}
	}

	return JSON.stringify(genHeaders, null, 2);
}

export async function genExample(fn: string, headers: Array<string>, schemaInst: telepact.TelepactSchema) {
	const example = schemaInst.parsed[fn].generateRandomValue(
		null,
		false,
		[],
		new _internal.GenerateContext(true, true, true, fn, random)
	);

	const requestHeaders: Record<string, any> = {};
	for (const header of headers) {
		requestHeaders[header] = schemaInst.parsedRequestHeaders[header]?.typeDeclaration?.generateRandomValue(
			null,
			false,
			new _internal.GenerateContext(true, true, true, fn, random)
		);
	}

	const request = [requestHeaders, example];
	const requestJson = JSON.stringify(request, null, 2);
	const requestBytes = new TextEncoder().encode(requestJson);

	const mockServerOptions = new telepact.MockServerOptions();
	const mockTelepact = new telepact.MockTelepactSchema(
		schemaInst.original,
		schemaInst.full,
		schemaInst.parsed,
		schemaInst.parsedRequestHeaders,
		schemaInst.parsedResponseHeaders
	);
	const mockServer = new telepact.MockServer(mockTelepact, mockServerOptions);

	const r = await mockServer.process(requestBytes);
	const responseBytes = r.bytes as Uint8Array;

	try {
		const responseJson = new TextDecoder().decode(responseBytes);
		const response = JSON.parse(responseJson);
		const finalResponseJson = JSON.stringify(response, null, 2);
		return {
			request: requestJson,
			response: finalResponseJson
		};
	} catch {
		const hexResponse = Array.from(responseBytes)
			.map((byte, index) => {
				const char =
					byte >= 32 && byte <= 126
						? String.fromCharCode(byte)
						: '0x' + byte.toString(16).padStart(2, '0');
				const newline = (index + 1) % 16 === 0 ? '\n' : '';
				return char + newline;
			})
			.join('');

		return {
			request: requestJson,
			response: hexResponse
		};
	}
}

function lastChar(str: string) {
	return str[str.length - 1] ?? '';
}

export function parseTelepactSchema(
	_schema: any[],
	schemaInst: telepact.TelepactSchema,
	sortDocCardsAZ: boolean,
	showInternalApi: boolean
): TypeData[] {
	const pseudoJson: Record<string, any>[] = showInternalApi ? schemaInst.full : schemaInst.original;

	const preppedPseudoJson = pseudoJson.map((e) => [findSchemaKey(e), e] as [string, any]);

	const availableErrors = preppedPseudoJson
		.filter(([schemaKey]) => schemaKey.startsWith('errors'))
		.map(([schemaKey, def]) => {
			const doc = def['///'];
			return {
				name: schemaKey,
				doc: doc,
				data: def[schemaKey]
			} as UnionTagTypeData;
		});

	const results: TypeData[] = preppedPseudoJson.map(([schemaKey, def]) => {
		let data: any;

		if (schemaKey.startsWith('union')) {
			data = def[schemaKey].map((tagDef: any) => {
				const enumTag = Object.keys(tagDef).find((k) => k !== '///') as string;
				const doc = tagDef['///'];
				return {
					name: enumTag,
					doc: doc,
					data: tagDef[enumTag]
				} as UnionTagTypeData;
			});
		} else if (schemaKey.startsWith('error')) {
			data = def[schemaKey].map((tagDef: any) => {
				const enumTag = Object.keys(tagDef).find((k) => k !== '///') as string;
				const doc = tagDef['///'];
				return {
					name: enumTag,
					doc: doc,
					data: tagDef[enumTag]
				} as UnionTagTypeData;
			});
		} else if (schemaKey.startsWith('fn')) {
			const argData = def[schemaKey];
			const resultData = def['->'].map((tagDef: any) => {
				const enumTag = Object.keys(tagDef).find((k) => k !== '///') as string;
				const doc = tagDef['///'];
				return {
					name: enumTag,
					doc: doc,
					data: tagDef[enumTag]
				} as UnionTagTypeData;
			});

			const exampleCall = schemaInst.parsed[schemaKey].generateRandomValue(
				null,
				false,
				[],
				new _internal.GenerateContext(true, false, true, schemaKey, new telepact.RandomGenerator(2, 2))
			);
			const exampleCallJson = JSON.stringify([{}, exampleCall]);

			const errorsRegex = def['_errors'];
			const inheritedErrors = availableErrors.filter((e) => e.name.match(errorsRegex)).map((e) => e.name);

			data = {
				args: argData,
				results: resultData,
				errorRegex: errorsRegex,
				exampleCallJson: exampleCallJson,
				inheritedErrors: inheritedErrors
			};
		} else if (schemaKey.startsWith('headers')) {
			const requestData = def[schemaKey];
			const responseData = def['->'];
			data = {
				type: 'header',
				name: schemaKey,
				doc: def['///'],
				requestData,
				responseData
			} as HeaderData;
		} else {
			data = def[schemaKey];
		}

		return {
			name: schemaKey,
			doc: def['///'],
			data: data
		} as TypeData;
	});

	if (sortDocCardsAZ) {
		results.sort((a, b) => {
			const tokens1 = a.name.split('.');
			const tokens2 = b.name.split('.');
			const key1 = tokens1[1] ?? '';
			const key2 = tokens2[1] ?? '';
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

	for (const key of Object.keys(definition)) {
		if (key.match(regex)) {
			matches.push(key);
		}
	}

	const result = matches[0];

	if (matches.length === 1 && result != undefined) {
		return result;
	}

	throw new Error(`Could not find schema key ${JSON.stringify(definition)} with regex ${regex}`);
}
