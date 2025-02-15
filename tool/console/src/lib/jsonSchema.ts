import { findSchemaKey } from '$lib';
import type { UApiSchema } from 'uapi';

export function createJsonSchema(uapi: UApiSchema): Record<string, any> {
	let original = uapi.full;

	const definitions: any = {};

	function convertType(uapiType: any): any {
		if (Array.isArray(uapiType)) {
			const [type, subType] = uapiType;
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
		} else if (typeof uapiType === 'object') {
			const properties: any = {};
			for (const key in uapiType) {
				properties[key] = convertType(uapiType[key]);
			}
			return { type: 'object', properties, additionalProperties: false };
		} else {
			return { type: uapiType };
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
