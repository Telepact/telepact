import type { UApiSchema } from 'uapi';

export function createJsonSchema(uapi: UApiSchema): string {
	let original = uapi.original;

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
					if (type.startsWith('struct.')) {
						return { $ref: `#/$defs/${type}` };
					}
					return { type };
			}
		} else if (typeof uapiType === 'object') {
			const properties: any = {};
			for (const key in uapiType) {
				properties[key] = convertType(uapiType[key]);
			}
			return { type: 'object', properties };
		} else {
			return { type: uapiType };
		}
	}

	const jsonSchema: any = {
		$schema: 'http://json-schema.org/draft-07/schema#',
		type: 'array',
		prefixItems: [{ type: 'object' }, { $ref: '#/$defs/fn.ping_' }],
		$defs: definitions
	};

	for (const item of original) {
		for (const key in item) {
			if (
				key.startsWith('headers.') ||
				key.startsWith('union.') ||
				key.startsWith('struct.') ||
				key.startsWith('errors.')
			) {
				definitions[key] = convertType(item[key]);
			} else if (key.startsWith('fn.')) {
				definitions[key] = {
					type: 'object',
					properties: {
						[key]: convertType(item[key])
					}
				};
			}
		}
	}

	console.log(JSON.stringify(jsonSchema, null, 2));

	return jsonSchema;
}
