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

import { RandomGenerator } from '../RandomGenerator.js';
import { TelepactSchema } from '../TelepactSchema.js';
import { encodeBase64 } from './binary/Base64Util.js';
import { GenerateContext } from './generation/GenerateContext.js';
import { TFieldDeclaration } from './types/TFieldDeclaration.js';
import { TType } from './types/TType.js';

const EXAMPLE_COLLECTION_LENGTH = 2;

export function getApiDefinitionsWithExamples(telepactSchema: TelepactSchema, includeInternal: boolean): any[] {
    const definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
    const defaultFnScope = getDefaultFnScope(telepactSchema.parsed);

    return definitions.map((definition) =>
        addExamplesToDefinition(definition as Record<string, any>, telepactSchema, defaultFnScope)
    );
}

function addExamplesToDefinition(
    definition: Record<string, any>,
    telepactSchema: TelepactSchema,
    defaultFnScope: string,
): Record<string, any> {
    const schemaKey = getSchemaKey(definition);
    const clonedDefinition = { ...definition };

    if (schemaKey.startsWith('info.')) {
        clonedDefinition.example = {};
        return clonedDefinition;
    }

    const randomGenerator = new RandomGenerator(EXAMPLE_COLLECTION_LENGTH, EXAMPLE_COLLECTION_LENGTH);

    if (schemaKey.startsWith('fn.')) {
        const ctx = new GenerateContext(true, false, true, schemaKey, randomGenerator);
        clonedDefinition.inputExample = normalizeExampleValue(
            telepactSchema.parsed[schemaKey].generateRandomValue(null, false, [], ctx),
        );
        clonedDefinition.outputExample = normalizeExampleValue(
            telepactSchema.parsed[`${schemaKey}.->`].generateRandomValue(null, false, [], ctx),
        );
        return clonedDefinition;
    }

    if (schemaKey.startsWith('headers.')) {
        const ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
        clonedDefinition.inputExample = generateHeaderExample(
            definition[schemaKey] as Record<string, any>,
            telepactSchema.parsedRequestHeaders,
            ctx,
        );
        clonedDefinition.outputExample = generateHeaderExample(
            definition['->'] as Record<string, any>,
            telepactSchema.parsedResponseHeaders,
            ctx,
        );
        return clonedDefinition;
    }

    if (schemaKey.startsWith('errors.')) {
        const ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
        clonedDefinition.example = generateRawUnionExample(definition[schemaKey] as any[], telepactSchema, ctx);
        return clonedDefinition;
    }

    const ctx = new GenerateContext(true, false, true, defaultFnScope, randomGenerator);
    clonedDefinition.example = normalizeExampleValue(
        telepactSchema.parsed[schemaKey].generateRandomValue(null, false, [], ctx),
    );
    return clonedDefinition;
}

function generateHeaderExample(
    headerDefinition: Record<string, any> | undefined,
    parsedHeaders: Record<string, TFieldDeclaration>,
    ctx: GenerateContext,
): Record<string, any> {
    const example: Record<string, any> = {};

    for (const headerName of Object.keys(headerDefinition || {}).sort()) {
        example[headerName] = normalizeExampleValue(
            parsedHeaders[headerName].typeDeclaration.generateRandomValue(null, false, ctx),
        );
    }

    return example;
}

function generateRawUnionExample(unionDefinition: any[], telepactSchema: TelepactSchema, ctx: GenerateContext): Record<string, any> {
    const tags = unionDefinition
        .map((tagDefinition) => {
            const [tagName, tagPayload] = Object.entries(tagDefinition as Record<string, any>)
                .find(([key]) => key !== '///') as [string, Record<string, any>];
            return [tagName, tagPayload] as [string, Record<string, any>];
        })
        .sort(([left], [right]) => left.localeCompare(right));
    const [tagName, tagPayload] = tags[ctx.randomGenerator.nextIntWithCeiling(tags.length)];
    return {
        [tagName]: generateRawStructExample(tagPayload, telepactSchema, ctx),
    };
}

function generateRawStructExample(
    structDefinition: Record<string, any>,
    telepactSchema: TelepactSchema,
    ctx: GenerateContext,
): Record<string, any> {
    const example: Record<string, any> = {};

    for (const fieldName of Object.keys(structDefinition).sort()) {
        const optional = fieldName.endsWith('!');
        if (optional) {
            if (!ctx.includeOptionalFields || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                continue;
            }
        } else if (!ctx.alwaysIncludeRequiredFields && ctx.randomGenerator.nextBoolean()) {
            continue;
        }

        example[fieldName] = generateRawTypeExample(structDefinition[fieldName], telepactSchema, ctx);
    }

    return example;
}

function generateRawTypeExample(typeExpression: any, telepactSchema: TelepactSchema, ctx: GenerateContext): any {
    if (typeof typeExpression === 'string') {
        const nullable = typeExpression.endsWith('?');
        const nonNullableTypeExpression = nullable ? typeExpression.slice(0, -1) : typeExpression;
        if (nullable && ctx.randomGenerator.nextBoolean()) {
            return null;
        }

        switch (nonNullableTypeExpression) {
            case 'boolean':
                return ctx.randomGenerator.nextBoolean();
            case 'integer':
                return ctx.randomGenerator.nextInt();
            case 'number':
                return ctx.randomGenerator.nextDouble();
            case 'string':
                return ctx.randomGenerator.nextString();
            case 'any': {
                const selectType = ctx.randomGenerator.nextIntWithCeiling(3);
                if (selectType === 0) {
                    return ctx.randomGenerator.nextBoolean();
                }
                if (selectType === 1) {
                    return ctx.randomGenerator.nextInt();
                }
                return ctx.randomGenerator.nextString();
            }
            case 'bytes':
                return encodeBase64(ctx.randomGenerator.nextBytes());
            default:
                return normalizeExampleValue(
                    telepactSchema.parsed[nonNullableTypeExpression].generateRandomValue(null, false, [], ctx),
                );
        }
    }

    if (Array.isArray(typeExpression)) {
        const length = ctx.randomGenerator.nextCollectionLength();
        const example = [];
        for (let i = 0; i < length; i += 1) {
            example.push(generateRawTypeExample(typeExpression[0], telepactSchema, ctx));
        }
        return example;
    }

    if (typeof typeExpression === 'object' && typeExpression !== null) {
        const objectDefinition = typeExpression as Record<string, any>;
        const [key] = Object.keys(objectDefinition);
        if (key === 'string') {
            const length = ctx.randomGenerator.nextCollectionLength();
            const example: Record<string, any> = {};
            for (let i = 0; i < length; i += 1) {
                example[ctx.randomGenerator.nextString()] = generateRawTypeExample(objectDefinition[key], telepactSchema, ctx);
            }
            return example;
        }
    }

    return null;
}

function normalizeExampleValue(value: any): any {
    if (value instanceof Uint8Array) {
        return encodeBase64(value);
    }

    if (Array.isArray(value)) {
        return value.map((entry) => normalizeExampleValue(entry));
    }

    if (typeof value === 'object' && value !== null) {
        const normalized: Record<string, any> = {};
        for (const [key, entry] of Object.entries(value)) {
            normalized[key] = normalizeExampleValue(entry);
        }
        return normalized;
    }

    return value;
}

function getDefaultFnScope(parsedTypes: Record<string, TType>): string {
    const nonInternalFunctions = Object.keys(parsedTypes)
        .filter((schemaKey) => schemaKey.startsWith('fn.') && !schemaKey.endsWith('.->') && !schemaKey.endsWith('_'))
        .sort();
    if (nonInternalFunctions.length > 0) {
        return nonInternalFunctions[0];
    }

    const allFunctions = Object.keys(parsedTypes)
        .filter((schemaKey) => schemaKey.startsWith('fn.') && !schemaKey.endsWith('.->'))
        .sort();
    if (allFunctions.length > 0) {
        return allFunctions[0];
    }

    return 'fn.ping_';
}

function getSchemaKey(definition: Record<string, any>): string {
    for (const key of Object.keys(definition)) {
        if (key !== '///' && key !== '->' && key !== '_errors') {
            return key;
        }
    }

    throw new Error(`Schema entry has no schema key: ${JSON.stringify(definition)}`);
}
