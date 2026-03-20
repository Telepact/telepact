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

import { LineCounter, parseDocument } from 'yaml';

import { Coordinates, DocumentLocator, Path } from './DocumentLocators';

type YamlDocument = { contents?: YamlNode | null; errors?: { message: string }[] };
type YamlNode = {
    constructor?: { name?: string };
    items?: YamlNode[];
    key?: YamlNode;
    range?: [number, number, number] | [number, number];
    value?: unknown;
};

function serializePath(path: Path): string {
    return JSON.stringify(path);
}

function getCoordinatesFromOffset(lineCounter: LineCounter, offset: number): Coordinates {
    const position = lineCounter.linePos(offset);
    return { row: position.line, col: position.col };
}

function getNodeCoordinates(lineCounter: LineCounter, node: YamlNode | null | undefined): Coordinates {
    const offset = node?.range?.[0];
    if (typeof offset === 'number') {
        return getCoordinatesFromOffset(lineCounter, offset);
    }
    return { row: 1, col: 1 };
}

function buildLocationsForNode(
    node: YamlNode | null | undefined,
    path: Path,
    lineCounter: LineCounter,
    locations: Record<string, Coordinates>,
): void {
    const kind = node?.constructor?.name;

    if (kind === 'YAMLSeq') {
        for (let index = 0; index < (node?.items?.length ?? 0); index += 1) {
            const item = node?.items?.[index];
            const itemPath = [...path, index];
            locations[serializePath(itemPath)] = getNodeCoordinates(lineCounter, item);
            buildLocationsForNode(item, itemPath, lineCounter, locations);
        }
        return;
    }

    if (kind === 'YAMLMap') {
        for (const pair of node?.items ?? []) {
            const key = pair.key?.value;
            if (typeof key !== 'string') {
                continue;
            }

            const keyPath = [...path, key];
            locations[serializePath(keyPath)] = getNodeCoordinates(lineCounter, pair.key);
            buildLocationsForNode(pair.value, keyPath, lineCounter, locations);
        }
    }
}

function validateNoDuplicateKeys(node: YamlNode | null | undefined): void {
    const kind = node?.constructor?.name;

    if (kind === 'YAMLSeq') {
        for (const item of node?.items ?? []) {
            validateNoDuplicateKeys(item);
        }
        return;
    }

    if (kind === 'YAMLMap') {
        const seenKeys = new Set<string>();
        for (const pair of node?.items ?? []) {
            const key = String(pair.key?.value);
            if (seenKeys.has(key)) {
                throw new Error('Duplicate YAML key');
            }
            seenKeys.add(key);
            validateNoDuplicateKeys(pair.value);
        }
    }
}

export function createDocumentLocatorFromYamlDocument(
    document: YamlDocument,
    lineCounter: LineCounter,
    text: string,
): DocumentLocator {
    if ((document.errors?.length ?? 0) > 0) {
        throw new Error(document.errors?.[0]?.message ?? 'YAML parse failed');
    }

    const locations: Record<string, Coordinates> = {};
    validateNoDuplicateKeys(document.contents);
    locations[serializePath([])] = getNodeCoordinates(lineCounter, document.contents);
    buildLocationsForNode(document.contents, [], lineCounter, locations);

    return (path: Path) => locations[serializePath(path)] ?? { row: 1, col: 1 };
}

export function createDocumentLocatorFromYamlText(text: string): DocumentLocator {
    const lineCounter = new LineCounter();
    const document = parseDocument(text, {
        lineCounter,
        merge: false,
        prettyErrors: false,
        strict: true,
    }) as unknown as YamlDocument;

    return createDocumentLocatorFromYamlDocument(document, lineCounter, text);
}
