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

import { format as prettierFormat, type Parser, type ParserOptions, type Plugin, type Printer, type SupportLanguage } from 'prettier';
import markdownPlugin from 'prettier/plugins/markdown';
import { parseDocument } from 'yaml';

type TelepactAst = {
    formattedText: string;
};

function indent(level: number): string {
    return '  '.repeat(level);
}

function isPlainKey(key: string): boolean {
    return /^(\/\/\/|->|[A-Za-z0-9_@.][A-Za-z0-9_@.!-]*)$/.test(key);
}

function formatKey(key: string): string {
    return isPlainKey(key) ? key : JSON.stringify(key);
}

function isTelepactFieldName(key: string): boolean {
    return /^@[a-z][a-zA-Z0-9_]*$/.test(key) || /^[a-z][a-zA-Z0-9_]*!?$/.test(key);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function splitLeadingPreamble(text: string): { preamble: string; body: string } {
    const normalizedText = text.replace(/\r\n/g, '\n');
    const match = normalizedText.match(/^(?:(?:[ \t]*#.*|[ \t]*)\n)*/);
    const preamble = match?.[0] ?? '';
    return {
        preamble,
        body: normalizedText.slice(preamble.length),
    };
}

function normalizeDocstringValue(value: unknown): string {
    if (Array.isArray(value)) {
        return value
            .map((entry) => String(entry).trim())
            .join('\n')
            .trim();
    }

    return String(value ?? '').trim();
}

async function formatDocstring(value: unknown, level: number): Promise<string> {
    const normalizedDocstring = normalizeDocstringValue(value);
    const formattedMarkdown = (
        await prettierFormat(normalizedDocstring, {
            parser: 'markdown',
            printWidth: 80,
            proseWrap: 'always',
            plugins: [markdownPlugin],
        })
    ).trimEnd();

    const lines = formattedMarkdown.length === 0 ? [''] : formattedMarkdown.split('\n');
    return ['|', ...lines.map((line) => `${indent(level + 1)}${line}`)].join('\n');
}

function formatInlineJson(value: unknown): string {
    if (Array.isArray(value)) {
        return `[${value.map((entry) => formatInlineJson(entry)).join(', ')}]`;
    }

    if (isPlainObject(value)) {
        const formattedEntries = Object.entries(value)
            .map(([key, entry]) => `${JSON.stringify(key)}: ${formatInlineJson(entry)}`)
            .join(', ');
        return `{${formattedEntries}}`;
    }

    return JSON.stringify(value);
}

function formatScalar(value: unknown): string {
    if (typeof value === 'string') {
        return `'${value.replace(/'/g, "''")}'`;
    }

    return JSON.stringify(value);
}

function isInlineScalar(value: unknown): boolean {
    return value === null || ['string', 'number', 'boolean'].includes(typeof value);
}

async function formatYamlValue(value: unknown, level: number, forceInlineJson = false): Promise<string> {
    if (forceInlineJson) {
        return formatInlineJson(value);
    }

    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '[]';
        }

        const lines: string[] = [];

        for (const entry of value) {
            if (isInlineScalar(entry)) {
                lines.push(`${indent(level)}- ${formatScalar(entry)}`);
                continue;
            }

            const formattedEntry = await formatYamlValue(entry, level + 1);
            const [firstLine, ...rest] = formattedEntry.split('\n');

            if (rest.length === 0) {
                lines.push(`${indent(level)}- ${firstLine.trimStart()}`);
                continue;
            }

            lines.push(`${indent(level)}- ${firstLine.trimStart()}`);
            lines.push(...rest);
        }

        return lines.join('\n');
    }

    if (isPlainObject(value)) {
        const entries = Object.entries(value);

        if (entries.length === 0) {
            return '{}';
        }

        const lines: string[] = [];

        for (const [key, entry] of entries) {
            const formattedKey = formatKey(key);

            if (key === '///') {
                const formattedDocstring = await formatDocstring(entry, level);
                const [firstLine, ...rest] = formattedDocstring.split('\n');
                lines.push(`${indent(level)}${formattedKey}: ${firstLine}`);
                lines.push(...rest);
                continue;
            }

            const useInlineJson = isTelepactFieldName(key);
            const isInlineCollection =
                (Array.isArray(entry) && entry.length === 0) ||
                (isPlainObject(entry) && Object.keys(entry).length === 0);

            if (useInlineJson || isInlineScalar(entry) || isInlineCollection) {
                lines.push(`${indent(level)}${formattedKey}: ${await formatYamlValue(entry, level + 1, useInlineJson)}`);
                continue;
            }

            lines.push(`${indent(level)}${formattedKey}:`);
            lines.push(await formatYamlValue(entry, level + 1, useInlineJson));
        }

        return lines.join('\n');
    }

    return formatScalar(value);
}

async function formatTelepactYaml(text: string): Promise<string> {
    const { preamble, body } = splitLeadingPreamble(text);
    const trimmedBody = body.trim();

    if (trimmedBody.length === 0) {
        return preamble.trimEnd().length === 0 ? '' : `${preamble.trimEnd()}\n`;
    }

    const document = parseDocument(trimmedBody);

    if (document.errors.length > 0) {
        throw document.errors[0];
    }

    const formattedBody = await formatYamlValue(document.toJSON(), 0);
    const normalizedPreamble = preamble.length === 0 ? '' : `${preamble.trimEnd()}\n\n`;

    return `${normalizedPreamble}${formattedBody}\n`;
}

const telepactParser: Parser<TelepactAst> = {
    astFormat: 'telepact-yaml',
    parse: async (text: string, _options: ParserOptions) => {
        return {
            formattedText: await formatTelepactYaml(text),
        };
    },
    locStart: () => 0,
    locEnd: (node) => node.formattedText.length,
};

const telepactPrinter: Printer<TelepactAst> = {
    print: (path) => path.getValue().formattedText,
};

const telepactLanguage: SupportLanguage = {
    name: 'telepact',
    parsers: ['telepact-parse'],
    extensions: ['.telepact.yaml', '.telepact.yml'],
};

const plugin: Plugin<TelepactAst> = {
    languages: [telepactLanguage],
    parsers: {
        'telepact-parse': telepactParser,
    },
    printers: {
        'telepact-yaml': telepactPrinter,
    },
};

export default plugin;
