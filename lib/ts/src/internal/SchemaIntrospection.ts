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

import { TelepactSchema } from '../TelepactSchema.js';

export function getIndexEntries(telepactSchema: TelepactSchema, includeInternal: boolean): Record<string, any>[] {
    const definitions = includeInternal ? telepactSchema.full : telepactSchema.original;

    return definitions
        .map((definition) => definition as Record<string, any>)
        .map((definition) => ({ definition, schemaKey: getSchemaKey(definition) }))
        .filter(({ schemaKey }) => schemaKey.startsWith('fn.') && !schemaKey.endsWith('.->'))
        .filter(({ schemaKey }) => includeInternal || !schemaKey.endsWith('_'))
        .map(({ definition, schemaKey }) => {
            const entry: Record<string, any> = { name: schemaKey };
            if (definition['///'] !== undefined) {
                entry['comment!'] = definition['///'];
            }
            return entry;
        });
}

export function getDefinitionClosure(
    telepactSchema: TelepactSchema,
    name: string,
    includeInternal: boolean,
): any[] {
    const definitionsByName = Object.fromEntries(
        telepactSchema.full.map((definition) => {
            const definitionRecord = definition as Record<string, any>;
            return [getSchemaKey(definitionRecord), definitionRecord];
        }),
    ) as Record<string, Record<string, any>>;
    const rootDefinition = getRootDefinition(telepactSchema, name, includeInternal);
    if (!rootDefinition) {
        return [];
    }

    const visited = new Set<string>();
    const visit = (schemaKey: string) => {
        if (visited.has(schemaKey)) {
            return;
        }

        const definition = definitionsByName[schemaKey];
        if (!definition) {
            return;
        }

        visited.add(schemaKey);
        for (const reference of getDefinitionReferences(definition, definitionsByName)) {
            visit(reference);
        }
    };

    visit(getSchemaKey(rootDefinition));

    return telepactSchema.full.filter((definition) =>
        visited.has(getSchemaKey(definition as Record<string, any>)),
    );
}

function getRootDefinition(
    telepactSchema: TelepactSchema,
    name: string,
    includeInternal: boolean,
): Record<string, any> | undefined {
    if (!includeInternal && name.endsWith('_')) {
        return undefined;
    }

    const definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
    return definitions
        .map((definition) => definition as Record<string, any>)
        .find((definition) => getSchemaKey(definition) === name);
}

function getDefinitionReferences(
    definition: Record<string, any>,
    definitionsByName: Record<string, Record<string, any>>,
): Set<string> {
    const references = new Set<string>();
    const schemaKey = getSchemaKey(definition);

    for (const [key, value] of Object.entries(definition)) {
        if (key === '///') {
            continue;
        }

        if (key === '_errors') {
            if (typeof value === 'string') {
                const regex = new RegExp(value);
                for (const candidate of Object.keys(definitionsByName)) {
                    if (regex.test(candidate)) {
                        references.add(candidate);
                    }
                }
            }
            continue;
        }

        if (key === schemaKey || key === '->') {
            for (const reference of getTypeExpressionReferences(value, definitionsByName)) {
                references.add(reference);
            }
        }
    }

    return references;
}

function getTypeExpressionReferences(
    typeExpression: any,
    definitionsByName: Record<string, Record<string, any>>,
): Set<string> {
    const references = new Set<string>();

    if (typeof typeExpression === 'string') {
        const schemaKey = typeExpression.endsWith('?')
            ? typeExpression.slice(0, -1)
            : typeExpression;
        if (definitionsByName[schemaKey]) {
            references.add(schemaKey);
        }
        return references;
    }

    if (Array.isArray(typeExpression)) {
        if (isUnionDefinition(typeExpression)) {
            for (const tagDefinition of typeExpression) {
                for (const [key, value] of Object.entries(tagDefinition as Record<string, any>)) {
                    if (key === '///') {
                        continue;
                    }
                    for (const reference of getTypeExpressionReferences(value, definitionsByName)) {
                        references.add(reference);
                    }
                }
            }
        } else if (typeExpression.length > 0) {
            for (const reference of getTypeExpressionReferences(typeExpression[0], definitionsByName)) {
                references.add(reference);
            }
        }
        return references;
    }

    if (typeof typeExpression === 'object' && typeExpression !== null) {
        const objectDefinition = typeExpression as Record<string, any>;
        if (Object.keys(objectDefinition).length === 1 && objectDefinition.string !== undefined) {
            for (const reference of getTypeExpressionReferences(objectDefinition.string, definitionsByName)) {
                references.add(reference);
            }
            return references;
        }

        for (const value of Object.values(objectDefinition)) {
            for (const reference of getTypeExpressionReferences(value, definitionsByName)) {
                references.add(reference);
            }
        }
    }

    return references;
}

function isUnionDefinition(typeExpression: any[]): boolean {
    if (typeExpression.length === 0) {
        return false;
    }

    return typeExpression.every((entry) => {
        if (typeof entry !== 'object' || entry === null || Array.isArray(entry)) {
            return false;
        }

        const nonCommentKeys = Object.keys(entry).filter((key) => key !== '///');
        return nonCommentKeys.length === 1 && typeof (entry as Record<string, any>)[nonCommentKeys[0]] === 'object';
    });
}

function getSchemaKey(definition: Record<string, any>): string {
    for (const key of Object.keys(definition)) {
        if (key !== '///' && key !== '->' && key !== '_errors') {
            return key;
        }
    }

    throw new Error(`Schema entry has no schema key: ${JSON.stringify(definition)}`);
}
