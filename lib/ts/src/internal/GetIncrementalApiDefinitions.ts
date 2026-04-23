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
import { getSchemaKey } from './GetApiDefinitionsWithExamples.js';

const ENTRYPOINT_PREFIXES = ['info.', 'headers.', 'errors.', 'fn.'];
const CUSTOM_TYPE_PREFIXES = ['fn.', 'struct.', 'union.', 'headers.', 'errors.', 'info.', '_ext.'];

export function getApiEntrypointDefinitions(telepactSchema: TelepactSchema, includeInternal: boolean): any[] {
    const definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
    return definitions.filter((definition) =>
        ENTRYPOINT_PREFIXES.some((prefix) => getSchemaKey(definition as Record<string, any>).startsWith(prefix)),
    );
}

export function getApiDefinitionsBySchemaKey(
    telepactSchema: TelepactSchema,
    schemaKey: string,
    includeInternal: boolean,
): any[] | null {
    const definitions = includeInternal ? telepactSchema.full : telepactSchema.original;
    const definitionsByKey = Object.fromEntries(
        definitions.map((definition) => [getSchemaKey(definition as Record<string, any>), definition as Record<string, any>]),
    ) as Record<string, Record<string, any>>;
    if (!(schemaKey in definitionsByKey)) {
        return null;
    }

    const includedSchemaKeys = new Set<string>();
    const pendingSchemaKeys = [schemaKey];
    while (pendingSchemaKeys.length > 0) {
        const currentSchemaKey = pendingSchemaKeys.pop() as string;
        if (includedSchemaKeys.has(currentSchemaKey)) {
            continue;
        }

        const definition = definitionsByKey[currentSchemaKey];
        if (definition === undefined) {
            continue;
        }

        includedSchemaKeys.add(currentSchemaKey);
        for (const referencedSchemaKey of getReferencedSchemaKeys(definition, definitionsByKey)) {
            if (!includedSchemaKeys.has(referencedSchemaKey)) {
                pendingSchemaKeys.push(referencedSchemaKey);
            }
        }
    }

    return definitions.filter((definition) =>
        includedSchemaKeys.has(getSchemaKey(definition as Record<string, any>))
    );
}

function getReferencedSchemaKeys(
    definition: Record<string, any>,
    definitionsByKey: Record<string, Record<string, any>>,
): string[] {
    const references = new Set<string>();
    for (const [key, value] of Object.entries(definition)) {
        if (key === '///' || key === '_errors') {
            continue;
        }
        collectReferencedSchemaKeys(value, definitionsByKey, references);
    }

    if (typeof definition._errors === 'string') {
        const regex = new RegExp(definition._errors);
        for (const schemaKey of Object.keys(definitionsByKey)) {
            if (regex.test(schemaKey)) {
                references.add(schemaKey);
            }
        }
    }

    return [...references].sort();
}

function collectReferencedSchemaKeys(
    value: any,
    definitionsByKey: Record<string, Record<string, any>>,
    references: Set<string>,
): void {
    if (typeof value === 'string') {
        const schemaKey = value.endsWith('?') ? value.slice(0, -1) : value;
        if (CUSTOM_TYPE_PREFIXES.some((prefix) => schemaKey.startsWith(prefix)) && schemaKey in definitionsByKey) {
            references.add(schemaKey);
        }
        return;
    }

    if (Array.isArray(value)) {
        for (const entry of value) {
            collectReferencedSchemaKeys(entry, definitionsByKey, references);
        }
        return;
    }

    if (typeof value === 'object' && value !== null) {
        for (const [key, entry] of Object.entries(value)) {
            if (key === '///') {
                continue;
            }
            collectReferencedSchemaKeys(entry, definitionsByKey, references);
        }
    }
}
