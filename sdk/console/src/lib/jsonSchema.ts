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

import { findSchemaKey } from '$lib';
import type { TelepactSchema } from './telepact/index.esm';

export function createJsonSchema(telepact: TelepactSchema): Record<string, any> {
	let original = telepact.full;

	const definitions: any = {};

	function convertType(telepactType: any): any {
		if (Array.isArray(telepactType)) {
			const [type, subType] = telepactType;
			switch (type) {
				case 'array':
					return { type: 'array', items: convertType(subType) };
				case 'object':
					return { type: 'object', additionalProperties: convertType(subType) };
				default:
					console.log('array type', type);
					if (type.startsWith('struct.')) {
						return { $ref: `#/$defs/${type}` };
					} else if (type.startsWith('union.')) {
						return { $ref: `#/$defs/${type}` };
					} else if (type.startsWith('fn')) {
						return { $ref: `#/$defs/${type}` };
					} else if (type.startsWith('headers.')) {
						return { $ref: `#/$defs/${type}` };
					} else if (type.startsWith('_ext.')) {
						return {};
					}
					return { type };
			}
		} else if (typeof telepactType === 'object') {
			const properties: any = {};
			for (const key in telepactType) {
				properties[key] = convertType(telepactType[key]);
			}
			return { type: 'object', properties, additionalProperties: false };
		} else {
			return { type: telepactType };
		}
	}

	const headers = {};
	const functions = [];

	for (const item of original) {
		var schemaKey = findSchemaKey(item);
		console.log('schemaKey', schemaKey);

		if (schemaKey.startsWith('struct.')) {
			definitions[schemaKey] = convertType(item[schemaKey]);
		} else if (schemaKey.startsWith('union.')) {
			definitions[schemaKey] = {
				oneOf: item[schemaKey].map((type: any) => {
					let tag = Object.keys(type).filter((k) => k !== '///')[0];
					return {
						type: 'object',
						required: [tag],
						properties: {
							[tag]: convertType(type[tag])
						}
					};
				})
			};
		} else if (schemaKey.startsWith('errors.')) {
			definitions[schemaKey] = {
				oneOf: item[schemaKey].map((type: any) => {
					let tag = Object.keys(type).filter((k) => k !== '///')[0];
					return {
						type: 'object',
						required: [tag],
						properties: {
							[tag]: convertType(type[tag])
						}
					};
				})
			};
		} else if (schemaKey.startsWith('fn.')) {
			functions.push(schemaKey);
			definitions[schemaKey] = {
				type: 'object',
				properties: {
					[schemaKey]: convertType(item[schemaKey])
				},
				additionalProperties: false
			};
		} else if (schemaKey.startsWith('headers.')) {
			let theseHeaders = item[schemaKey];
			Object.assign(headers, theseHeaders);
		} else if (schemaKey.startsWith('_ext.')) {
			definitions[schemaKey] = convertType(item[schemaKey]);
		}
	}

	const allHeaders: Record<string, any> = {};
	Object.entries(headers).forEach(([header, type]) => {
		allHeaders[header] = convertType(type);
	});

	const oneOfEachFunctions = {
		oneOf: functions.map((fn) => ({ $ref: `#/$defs/${fn}` }))
	};

	const jsonSchema: any = {
		$schema: '"https://json-schema.org/draft/2020-12/schema"',
		type: 'array',
		prefixItems: [
			{
				type: 'object',
				properties: allHeaders,
				additionalProperties: true
			},
			oneOfEachFunctions
		],
		$defs: definitions
	};

	console.log(JSON.stringify(jsonSchema, null, 2));

	return jsonSchema;
}
