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

import { Coordinates, DocumentLocator, Path } from './DocumentLocators';

type ParsedNode = { value: any; nextIndex: number };
type LineInfo = {
    index: number;
    indent: number;
    content: string;
    trimmed: string;
};
type ParsedInlineEntry = {
    key: string;
    keyColumn: number;
    valueText: string;
    valueColumn: number;
};

function serializePath(path: Path): string {
    return JSON.stringify(path);
}

function normalizeDocument(text: string): string {
    return text.replace(/\r\n?/g, '\n');
}

function trimComment(text: string): string {
    let quote: '"' | "'" | null = null;
    for (let index = 0; index < text.length; index += 1) {
        const c = text[index];
        if (c === '"' || c === "'") {
            if (quote === c) {
                quote = null;
            } else if (quote === null) {
                quote = c;
            }
            continue;
        }
        if (quote === null && c === '#') {
            return text.slice(0, index).trimEnd();
        }
    }
    return text.trimEnd();
}

function countIndent(line: string): number {
    let indent = 0;
    while (indent < line.length && line[indent] === ' ') {
        indent += 1;
    }
    return indent;
}

function getLineInfo(lines: string[], index: number): LineInfo {
    const rawLine = lines[index];
    const content = trimComment(rawLine);
    return {
        index,
        indent: countIndent(rawLine),
        content,
        trimmed: content.trim(),
    };
}

function peekSignificantLine(lines: string[], startIndex: number): LineInfo | null {
    for (let index = startIndex; index < lines.length; index += 1) {
        const info = getLineInfo(lines, index);
        if (info.trimmed !== '') {
            return info;
        }
    }
    return null;
}

function rejectUnsupportedYaml(line: string): void {
    const trimmed = trimComment(line).trim();
    if (trimmed === '') {
        return;
    }
    if (trimmed === '---' || trimmed === '...') {
        throw new Error('YAML multi-document markers are not supported');
    }
    if (/^\s*[&*]/.test(line) || /:\s*[&*]/.test(line) || /-\s*[&*]/.test(line)) {
        throw new Error('YAML anchors and aliases are not supported');
    }
    if (/^\s*!/.test(line) || /:\s*!/.test(line) || /-\s*!/.test(line)) {
        throw new Error('YAML tags are not supported');
    }
    if (trimmed.includes('<<:')) {
        throw new Error('YAML merge keys are not supported');
    }
}

function decodeQuotedString(text: string): string {
    if (text.startsWith('"')) {
        return JSON.parse(text);
    }

    let result = '';
    for (let index = 1; index < text.length - 1; index += 1) {
        const c = text[index];
        if (c === "'" && text[index + 1] === "'") {
            result += "'";
            index += 1;
        } else {
            result += c;
        }
    }
    return result;
}

function parseScalar(text: string): any {
    if (text === 'null') {
        return null;
    }
    if (text === 'true') {
        return true;
    }
    if (text === 'false') {
        return false;
    }
    if (/^-?(0|[1-9][0-9]*)$/.test(text)) {
        return Number.parseInt(text, 10);
    }
    if (/^-?(0|[1-9][0-9]*)\.[0-9]+$/.test(text)) {
        return Number.parseFloat(text);
    }
    if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
        return decodeQuotedString(text);
    }
    return text;
}

function parseKeyToken(text: string): string {
    const trimmed = text.trim();
    if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
        return decodeQuotedString(trimmed);
    }
    if (trimmed === '///' || trimmed === '->') {
        return trimmed;
    }
    if (!/^[A-Za-z][A-Za-z0-9_.!]*$/.test(trimmed)) {
        throw new Error('Invalid YAML key');
    }
    return trimmed;
}

function findMappingColon(text: string): number {
    let quote: '"' | "'" | null = null;
    for (let index = 0; index < text.length; index += 1) {
        const c = text[index];
        if (c === '"' || c === "'") {
            if (quote === c) {
                quote = null;
            } else if (quote === null) {
                quote = c;
            }
            continue;
        }
        if (quote === null && c === ':') {
            const next = text[index + 1];
            if (next === undefined || next === ' ') {
                return index;
            }
        }
    }
    return -1;
}

function parseInlineEntry(text: string, baseColumn: number): ParsedInlineEntry {
    const leadingSpaces = text.length - text.trimStart().length;
    const trimmed = text.trimStart();
    const colonIndex = findMappingColon(trimmed);
    if (colonIndex < 0) {
        throw new Error('Expected YAML mapping entry');
    }
    const keyText = trimmed.slice(0, colonIndex).trimEnd();
    const remainder = trimmed.slice(colonIndex + 1);
    const valueText = remainder.trimStart();
    const spacesBeforeValue = remainder.length - valueText.length;

    return {
        key: parseKeyToken(keyText),
        keyColumn: baseColumn + leadingSpaces,
        valueText,
        valueColumn: baseColumn + leadingSpaces + colonIndex + 1 + spacesBeforeValue,
    };
}

function startsFlowCollection(text: string): boolean {
    return text.startsWith('{') || text.startsWith('[');
}

function skipFlowWhitespace(text: string, index: number): number {
    let current = index;
    while (current < text.length && text[current] === ' ') {
        current += 1;
    }
    return current;
}

function findFlowDelimiter(text: string, startIndex: number, delimiter: string): number {
    let quote: '"' | "'" | null = null;
    for (let index = startIndex; index < text.length; index += 1) {
        const c = text[index];
        if (c === '"' || c === "'") {
            if (quote === c) {
                quote = null;
            } else if (quote === null) {
                quote = c;
            }
            continue;
        }
        if (quote === null && c === delimiter) {
            return index;
        }
    }
    return -1;
}

function findFlowScalarEnd(text: string, startIndex: number): number {
    let quote: '"' | "'" | null = null;
    for (let index = startIndex; index < text.length; index += 1) {
        const c = text[index];
        if (c === '"' || c === "'") {
            if (quote === c) {
                quote = null;
            } else if (quote === null) {
                quote = c;
            }
            continue;
        }
        if (quote === null && (c === ',' || c === ']' || c === '}')) {
            return index;
        }
    }
    return text.length;
}

function parseFlowNode(
    text: string,
    startIndex: number,
    row: number,
    baseColumn: number,
    path: Path,
    locations: Record<string, Coordinates>,
): { value: any; nextIndex: number } {
    const index = skipFlowWhitespace(text, startIndex);
    if (index >= text.length) {
        throw new Error('Unexpected end of YAML flow collection');
    }

    if (text[index] === '[') {
        const value: any[] = [];
        let current = skipFlowWhitespace(text, index + 1);
        if (text[current] === ']') {
            return { value, nextIndex: current + 1 };
        }

        while (current < text.length) {
            const itemPath = [...path, value.length];
            locations[serializePath(itemPath)] = { row, col: baseColumn + current };
            const parsed = parseFlowNode(text, current, row, baseColumn, itemPath, locations);
            value.push(parsed.value);
            current = skipFlowWhitespace(text, parsed.nextIndex);
            if (text[current] === ',') {
                current = skipFlowWhitespace(text, current + 1);
                continue;
            }
            if (text[current] === ']') {
                return { value, nextIndex: current + 1 };
            }
            break;
        }
        throw new Error('Invalid YAML flow collection');
    }

    if (text[index] === '{') {
        const value: Record<string, any> = {};
        let current = skipFlowWhitespace(text, index + 1);
        if (text[current] === '}') {
            return { value, nextIndex: current + 1 };
        }

        while (current < text.length) {
            const keyStart = current;
            const colonIndex = findFlowDelimiter(text, keyStart, ':');
            if (colonIndex < 0) {
                throw new Error('Expected YAML mapping entry');
            }
            const keyText = text.slice(keyStart, colonIndex).trimEnd();
            const key = parseKeyToken(keyText);
            const keyPath = [...path, key];
            const serializedPath = serializePath(keyPath);
            if (serializedPath in locations || Object.prototype.hasOwnProperty.call(value, key)) {
                throw new Error('Duplicate YAML key');
            }
            locations[serializedPath] = { row, col: baseColumn + keyStart };

            current = skipFlowWhitespace(text, colonIndex + 1);
            const parsed = parseFlowNode(text, current, row, baseColumn, keyPath, locations);
            value[key] = parsed.value;
            current = skipFlowWhitespace(text, parsed.nextIndex);
            if (text[current] === ',') {
                current = skipFlowWhitespace(text, current + 1);
                continue;
            }
            if (text[current] === '}') {
                return { value, nextIndex: current + 1 };
            }
            break;
        }
        throw new Error('Invalid YAML flow collection');
    }

    const endIndex = findFlowScalarEnd(text, index);
    return { value: parseScalar(text.slice(index, endIndex).trim()), nextIndex: endIndex };
}

function parseBlockScalar(
    lines: string[],
    startIndex: number,
    parentIndent: number,
    folded: boolean,
): ParsedNode {
    let index = startIndex;
    const blockLines: string[] = [];
    let minIndent: number | null = null;

    while (index < lines.length) {
        const info = getLineInfo(lines, index);
        if (info.trimmed !== '' && info.indent <= parentIndent) {
            break;
        }
        if (info.trimmed !== '') {
            minIndent = minIndent === null ? info.indent : Math.min(minIndent, info.indent);
        }
        blockLines.push(lines[index]);
        index += 1;
    }

    const contentIndent = minIndent ?? (parentIndent + 1);
    const normalizedLines = blockLines.map((line) => {
        if (trimComment(line).trim() === '') {
            return '';
        }
        return line.slice(Math.min(contentIndent, line.length));
    });

    if (!folded) {
        return { value: normalizedLines.join('\n'), nextIndex: index };
    }

    let value = '';
    for (const line of normalizedLines) {
        if (line === '') {
            value += '\n';
            continue;
        }
        if (value !== '' && !value.endsWith('\n')) {
            value += ' ';
        }
        value += line;
    }
    return { value, nextIndex: index };
}

function parseValueText(
    lines: string[],
    info: LineInfo,
    currentIndent: number,
    path: Path,
    valueText: string,
    valueColumn: number,
    locations: Record<string, Coordinates>,
): ParsedNode {
    if (valueText === '{}') {
        return { value: {}, nextIndex: info.index + 1 };
    }
    if (valueText === '[]') {
        return { value: [], nextIndex: info.index + 1 };
    }
    if (valueText === '|') {
        return parseBlockScalar(lines, info.index + 1, currentIndent, false);
    }
    if (valueText === '>') {
        return parseBlockScalar(lines, info.index + 1, currentIndent, true);
    }
    if (valueText === '') {
        const nextInfo = peekSignificantLine(lines, info.index + 1);
        if (nextInfo === null || nextInfo.indent <= currentIndent) {
            return { value: null, nextIndex: info.index + 1 };
        }
        return parseNode(lines, nextInfo.index, nextInfo.indent, path, locations);
    }
    if (startsFlowCollection(valueText)) {
        const parsed = parseFlowNode(valueText, 0, info.index + 1, valueColumn, path, locations);
        if (skipFlowWhitespace(valueText, parsed.nextIndex) !== valueText.length) {
            throw new Error('Invalid YAML flow collection');
        }
        return { value: parsed.value, nextIndex: info.index + 1 };
    }
    return { value: parseScalar(valueText), nextIndex: info.index + 1 };
}

function parseMapEntries(
    lines: string[],
    startIndex: number,
    indent: number,
    path: Path,
    locations: Record<string, Coordinates>,
    initialEntry?: { info: LineInfo; text: string; baseColumn: number },
): ParsedNode {
    const value: Record<string, any> = {};
    let lineIndex = startIndex;
    let firstEntry = initialEntry;

    while (true) {
        const info = firstEntry?.info ?? peekSignificantLine(lines, lineIndex);
        if (info === null) {
            break;
        }
        if (firstEntry === undefined && info.indent < indent) {
            break;
        }
        if (firstEntry === undefined && (info.indent !== indent || info.trimmed.startsWith('-'))) {
            if (firstEntry !== undefined) {
                throw new Error('Unexpected YAML mapping indentation');
            }
            break;
        }

        const entryText = firstEntry?.text ?? info.content.slice(indent);
        const baseColumn = firstEntry?.baseColumn ?? (indent + 1);
        const entry = parseInlineEntry(entryText, baseColumn);
        const keyPath = [...path, entry.key];
        const serializedPath = serializePath(keyPath);
        if (serializedPath in locations || Object.prototype.hasOwnProperty.call(value, entry.key)) {
            throw new Error('Duplicate YAML key');
        }
        locations[serializedPath] = { row: info.index + 1, col: entry.keyColumn };

        const parsedValue = parseValueText(lines, info, indent, keyPath, entry.valueText, entry.valueColumn, locations);
        value[entry.key] = parsedValue.value;
        lineIndex = parsedValue.nextIndex;
        firstEntry = undefined;
    }

    return { value, nextIndex: lineIndex };
}

function parseSequence(
    lines: string[],
    startIndex: number,
    indent: number,
    path: Path,
    locations: Record<string, Coordinates>,
): ParsedNode {
    const value: any[] = [];
    let lineIndex = startIndex;

    while (true) {
        const info = peekSignificantLine(lines, lineIndex);
        if (info === null) {
            break;
        }
        if (info.indent < indent) {
            break;
        }
        if (info.indent !== indent || !(info.trimmed === '-' || info.trimmed.startsWith('- '))) {
            break;
        }

        const itemPath = [...path, value.length];
        locations[serializePath(itemPath)] = { row: info.index + 1, col: indent + 1 };

        const afterDash = info.content.slice(indent + 1);
        const valueText = afterDash.trimStart();
        if (valueText === '') {
            const nextInfo = peekSignificantLine(lines, info.index + 1);
            if (nextInfo === null || nextInfo.indent <= indent) {
                value.push(null);
                lineIndex = info.index + 1;
                continue;
            }
            const parsedNode = parseNode(lines, nextInfo.index, nextInfo.indent, itemPath, locations);
            value.push(parsedNode.value);
            lineIndex = parsedNode.nextIndex;
            continue;
        }

        const valueColumn = indent + 2 + (afterDash.length - valueText.length);
        if (!startsFlowCollection(valueText) && findMappingColon(valueText) >= 0) {
            const parsedNode = parseMapEntries(lines, info.index + 1, indent + 2, itemPath, locations, {
                info,
                text: afterDash,
                baseColumn: indent + 2,
            });
            value.push(parsedNode.value);
            lineIndex = parsedNode.nextIndex;
            continue;
        }

        const parsedValue = parseValueText(lines, info, indent, itemPath, valueText, valueColumn, locations);
        value.push(parsedValue.value);
        lineIndex = parsedValue.nextIndex;
    }

    return { value, nextIndex: lineIndex };
}

function parseNode(
    lines: string[],
    startIndex: number,
    indent: number,
    path: Path,
    locations: Record<string, Coordinates>,
): ParsedNode {
    const info = peekSignificantLine(lines, startIndex);
    if (info === null) {
        throw new Error('Unexpected end of YAML document');
    }
    if (info.indent !== indent) {
        throw new Error('Unexpected YAML indentation');
    }
    if (info.trimmed === '-' || info.trimmed.startsWith('- ')) {
        return parseSequence(lines, startIndex, indent, path, locations);
    }
    return parseMapEntries(lines, startIndex, indent, path, locations);
}

function buildYamlLocations(text: string): Record<string, Coordinates> {
    const normalized = normalizeDocument(text);
    const lines = normalized.split('\n');
    for (const line of lines) {
        if (/^ *\t/.test(line)) {
            throw new Error('Tabs are not supported in Telepact YAML');
        }
        rejectUnsupportedYaml(line);
    }

    const locations: Record<string, Coordinates> = {};
    const firstInfo = peekSignificantLine(lines, 0);
    if (firstInfo === null) {
        throw new Error('YAML document cannot be empty');
    }
    if (firstInfo.indent !== 0) {
        throw new Error('YAML root indentation must start at column 1');
    }

    const parsed = parseNode(lines, firstInfo.index, 0, [], locations);
    if (!Array.isArray(parsed.value)) {
        throw new Error('Telepact YAML root must be a sequence');
    }
    return locations;
}

export function createPathDocumentYamlCoordinatesPseudoJsonLocator(text: string): DocumentLocator {
    const locations = buildYamlLocations(text);
    return (path: Path) => locations[serializePath(path)] ?? { row: 1, col: 1 };
}

export function getPathDocumentYamlCoordinatesPseudoJson(path: Path, document: string): Coordinates {
    return createPathDocumentYamlCoordinatesPseudoJsonLocator(document)(path);
}
