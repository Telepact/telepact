//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { LineCounter, parseDocument } from 'yaml';

import { DocumentLocator } from './DocumentLocators.js';
import { createDocumentLocatorFromYamlDocument } from './BuildDocumentLocatorFromYamlAst.js';

function normalizeJsonCompatibleValue(value: any): any {
    if (value === null || typeof value === 'string' || typeof value === 'boolean') {
        return value;
    }

    if (typeof value === 'number') {
        if (!Number.isFinite(value)) {
            throw new Error('YAML values must be JSON-compatible');
        }
        return value;
    }

    if (Array.isArray(value)) {
        return value.map(normalizeJsonCompatibleValue);
    }

    if (typeof value === 'object') {
        if (Object.getPrototypeOf(value) !== Object.prototype) {
            throw new Error('YAML values must be JSON-compatible');
        }

        const normalized: Record<string, any> = {};
        for (const [key, child] of Object.entries(value)) {
            normalized[key] = normalizeJsonCompatibleValue(child);
        }
        return normalized;
    }

    throw new Error('YAML values must be JSON-compatible');
}

export function parseTelepactYaml(text: string): { canonicalJsonText: string; locator?: DocumentLocator } {
    const lineCounter = new LineCounter();
    const document = parseDocument(text, {
        lineCounter,
        merge: false,
        prettyErrors: false,
        strict: true,
    });
    if (document.errors.length > 0) {
        throw new Error(document.errors[0].message);
    }

    const parsed = normalizeJsonCompatibleValue(document.toJS({ mapAsMap: false }));
    if (!Array.isArray(parsed)) {
        throw new Error('Telepact YAML root must be a sequence');
    }

    return {
        canonicalJsonText: JSON.stringify(parsed),
        locator: createDocumentLocatorFromYamlDocument(document as unknown as { contents?: unknown; errors?: { message: string }[] }, lineCounter, text),
    };
}
