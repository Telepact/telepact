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

package io.github.telepact.internal.schema;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.telepact.internal.schema.DocumentLocators.DocumentLocator;

public class GetPathDocumentYamlCoordinatesPseudoJson {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private record LineInfo(int index, int indent, String content, String trimmed) {}
    private record ParsedNode(Object value, int nextIndex) {}

    public static DocumentLocator createPathDocumentYamlCoordinatesPseudoJsonLocator(String text) throws Exception {
        final var normalized = text.replace("\r\n", "\n").replace('\r', '\n');
        final var lines = normalized.split("\n", -1);
        for (final var line : lines) {
            if (line.matches("^ *\\t.*")) {
                throw new IllegalArgumentException("Tabs are not supported in Telepact YAML");
            }
            rejectUnsupportedYaml(line);
        }

        final var firstInfo = peekSignificantLine(lines, 0);
        if (firstInfo == null || firstInfo.indent() != 0) {
            throw new IllegalArgumentException("Telepact YAML must start at the root sequence");
        }

        final Map<String, Map<String, Object>> locations = new HashMap<>();
        final var parsed = parseNode(lines, firstInfo.index(), 0, List.of(), locations);
        if (!(parsed.value() instanceof List<?>)) {
            throw new IllegalArgumentException("Telepact YAML root must be a sequence");
        }

        return path -> locations.getOrDefault(
                OBJECT_MAPPER.valueToTree(path).toString(),
                Map.of("row", 1, "col", 1));
    }

    public static Map<String, Object> getPathDocumentYamlCoordinatesPseudoJson(List<Object> path, String document) {
        try {
            return createPathDocumentYamlCoordinatesPseudoJsonLocator(document).locate(path);
        } catch (Exception e) {
            return Map.of("row", 1, "col", 1);
        }
    }

    private static ParsedNode parseNode(String[] lines, int startIndex, int indent, List<Object> path,
            Map<String, Map<String, Object>> locations) {
        final var info = peekSignificantLine(lines, startIndex);
        if (info == null || info.indent() != indent) {
            throw new IllegalArgumentException("Unexpected YAML indentation");
        }
        if (info.trimmed().equals("-") || info.trimmed().startsWith("- ")) {
            return parseSequence(lines, startIndex, indent, path, locations);
        }
        return parseMapEntries(lines, startIndex, indent, path, locations, null);
    }

    private static ParsedNode parseSequence(String[] lines, int startIndex, int indent, List<Object> path,
            Map<String, Map<String, Object>> locations) {
        final var value = new ArrayList<>();
        var lineIndex = startIndex;

        while (true) {
            final var info = peekSignificantLine(lines, lineIndex);
            if (info == null || info.indent() < indent) {
                break;
            }
            if (info.indent() != indent || !(info.trimmed().equals("-") || info.trimmed().startsWith("- "))) {
                break;
            }

            final var itemPath = new ArrayList<>(path);
            itemPath.add(value.size());
            locations.put(serializePath(itemPath), Map.of("row", info.index() + 1, "col", indent + 1));

            final var afterDash = info.content().substring(indent + 1);
            final var valueText = afterDash.stripLeading();
            if (valueText.isEmpty()) {
                final var nextInfo = peekSignificantLine(lines, info.index() + 1);
                if (nextInfo == null || nextInfo.indent() <= indent) {
                    value.add(null);
                    lineIndex = info.index() + 1;
                    continue;
                }
                final var parsed = parseNode(lines, nextInfo.index(), nextInfo.indent(), itemPath, locations);
                value.add(parsed.value());
                lineIndex = parsed.nextIndex();
                continue;
            }

            final var valueColumn = indent + 2 + (afterDash.length() - valueText.length());
            if (!startsFlowCollection(valueText) && findMappingColon(valueText) >= 0) {
                final var parsed = parseMapEntries(lines, info.index() + 1, indent + 2, itemPath, locations,
                        Map.of("info", info, "text", afterDash, "baseColumn", indent + 2));
                value.add(parsed.value());
                lineIndex = parsed.nextIndex();
                continue;
            }

            final var parsedValue = parseValueText(lines, info, indent, itemPath, valueText, valueColumn, locations);
            value.add(parsedValue.value());
            lineIndex = parsedValue.nextIndex();
        }

        return new ParsedNode(value, lineIndex);
    }

    private static ParsedNode parseMapEntries(String[] lines, int startIndex, int indent, List<Object> path,
            Map<String, Map<String, Object>> locations, Map<String, Object> initialEntry) {
        final var value = new HashMap<String, Object>();
        var lineIndex = startIndex;
        var firstEntry = initialEntry;

        while (true) {
            final LineInfo info;
            if (firstEntry != null) {
                info = (LineInfo) firstEntry.get("info");
            } else {
                info = peekSignificantLine(lines, lineIndex);
            }
            if (info == null) {
                break;
            }
            if (firstEntry == null && info.indent() < indent) {
                break;
            }
            if (firstEntry == null && (info.indent() != indent || info.trimmed().startsWith("-"))) {
                if (firstEntry != null) {
                    throw new IllegalArgumentException("Unexpected YAML mapping indentation");
                }
                break;
            }

            final var entryText = firstEntry != null ? (String) firstEntry.get("text") : info.content().substring(indent);
            final var baseColumn = firstEntry != null ? (Integer) firstEntry.get("baseColumn") : indent + 1;
            final var entry = parseInlineEntry(entryText, baseColumn);
            final var keyPath = new ArrayList<>(path);
            keyPath.add(entry.key);
            final var serializedPath = serializePath(keyPath);
            if (locations.containsKey(serializedPath) || value.containsKey(entry.key)) {
                throw new IllegalArgumentException("Duplicate YAML key");
            }
            locations.put(serializedPath, Map.of("row", info.index() + 1, "col", entry.keyColumn));

            final var parsedValue = parseValueText(lines, info, indent, keyPath, entry.valueText, entry.valueColumn, locations);
            value.put(entry.key, parsedValue.value());
            lineIndex = parsedValue.nextIndex();
            firstEntry = null;
        }

        return new ParsedNode(value, lineIndex);
    }

    private static ParsedNode parseValueText(String[] lines, LineInfo info, int currentIndent, List<Object> path,
            String valueText, int valueColumn, Map<String, Map<String, Object>> locations) {
        return switch (valueText) {
            case "{}" -> new ParsedNode(new HashMap<String, Object>(), info.index() + 1);
            case "[]" -> new ParsedNode(new ArrayList<Object>(), info.index() + 1);
            case "|" -> parseBlockScalar(lines, info.index() + 1, currentIndent, false);
            case ">" -> parseBlockScalar(lines, info.index() + 1, currentIndent, true);
            case "" -> {
                final var nextInfo = peekSignificantLine(lines, info.index() + 1);
                if (nextInfo == null || nextInfo.indent() <= currentIndent) {
                    yield new ParsedNode(null, info.index() + 1);
                }
                yield parseNode(lines, nextInfo.index(), nextInfo.indent(), path, locations);
            }
            default -> {
                if (startsFlowCollection(valueText)) {
                    final var parsed = parseFlowNode(valueText, 0, info.index() + 1, valueColumn, path, locations);
                    if (skipFlowWhitespace(valueText, parsed.nextIndex()) != valueText.length()) {
                        throw new IllegalArgumentException("Invalid YAML flow collection");
                    }
                    yield new ParsedNode(parsed.value(), info.index() + 1);
                }
                yield new ParsedNode(parseScalar(valueText), info.index() + 1);
            }
        };
    }

    private static ParsedNode parseBlockScalar(String[] lines, int startIndex, int parentIndent, boolean folded) {
        var index = startIndex;
        final var blockLines = new ArrayList<String>();
        Integer minIndent = null;
        while (index < lines.length) {
            final var info = getLineInfo(lines, index);
            if (!info.trimmed().isEmpty() && info.indent() <= parentIndent) {
                break;
            }
            if (!info.trimmed().isEmpty()) {
                minIndent = minIndent == null ? info.indent() : Math.min(minIndent, info.indent());
            }
            blockLines.add(lines[index]);
            index += 1;
        }

        final int contentIndent = minIndent == null ? parentIndent + 1 : minIndent;
        final var normalizedLines = new ArrayList<String>();
        for (final var line : blockLines) {
            if (trimComment(line).strip().isEmpty()) {
                normalizedLines.add("");
            } else {
                normalizedLines.add(line.substring(Math.min(contentIndent, line.length())));
            }
        }

        if (!folded) {
            return new ParsedNode(String.join("\n", normalizedLines), index);
        }

        final var builder = new StringBuilder();
        for (final var line : normalizedLines) {
            if (line.isEmpty()) {
                builder.append('\n');
            } else {
                if (builder.length() > 0 && builder.charAt(builder.length() - 1) != '\n') {
                    builder.append(' ');
                }
                builder.append(line);
            }
        }
        return new ParsedNode(builder.toString(), index);
    }

    private record FlowNode(Object value, int nextIndex) {}
    private record InlineEntry(String key, int keyColumn, String valueText, int valueColumn) {}

    private static boolean startsFlowCollection(String text) {
        return text.startsWith("{") || text.startsWith("[");
    }

    private static int skipFlowWhitespace(String text, int index) {
        var current = index;
        while (current < text.length() && text.charAt(current) == ' ') {
            current += 1;
        }
        return current;
    }

    private static int findFlowDelimiter(String text, int startIndex, char delimiter) {
        Character quote = null;
        for (int index = startIndex; index < text.length(); index += 1) {
            final var c = text.charAt(index);
            if (c == '"' || c == '\'') {
                quote = quote != null && quote == c ? null : (quote == null ? c : quote);
                continue;
            }
            if (quote == null && c == delimiter) {
                return index;
            }
        }
        return -1;
    }

    private static int findFlowScalarEnd(String text, int startIndex) {
        Character quote = null;
        for (int index = startIndex; index < text.length(); index += 1) {
            final var c = text.charAt(index);
            if (c == '"' || c == '\'') {
                quote = quote != null && quote == c ? null : (quote == null ? c : quote);
                continue;
            }
            if (quote == null && (c == ',' || c == ']' || c == '}')) {
                return index;
            }
        }
        return text.length();
    }

    private static FlowNode parseFlowNode(String text, int startIndex, int row, int baseColumn, List<Object> path,
            Map<String, Map<String, Object>> locations) {
        final var index = skipFlowWhitespace(text, startIndex);
        if (index >= text.length()) {
            throw new IllegalArgumentException("Unexpected end of YAML flow collection");
        }

        if (text.charAt(index) == '[') {
            final var value = new ArrayList<>();
            var current = skipFlowWhitespace(text, index + 1);
            if (current < text.length() && text.charAt(current) == ']') {
                return new FlowNode(value, current + 1);
            }

            while (current < text.length()) {
                final var itemPath = new ArrayList<>(path);
                itemPath.add(value.size());
                locations.put(serializePath(itemPath), Map.of("row", row, "col", baseColumn + current));
                final var parsed = parseFlowNode(text, current, row, baseColumn, itemPath, locations);
                value.add(parsed.value());
                current = skipFlowWhitespace(text, parsed.nextIndex());
                if (current < text.length() && text.charAt(current) == ',') {
                    current = skipFlowWhitespace(text, current + 1);
                    continue;
                }
                if (current < text.length() && text.charAt(current) == ']') {
                    return new FlowNode(value, current + 1);
                }
                break;
            }
            throw new IllegalArgumentException("Invalid YAML flow collection");
        }

        if (text.charAt(index) == '{') {
            final var value = new HashMap<String, Object>();
            var current = skipFlowWhitespace(text, index + 1);
            if (current < text.length() && text.charAt(current) == '}') {
                return new FlowNode(value, current + 1);
            }

            while (current < text.length()) {
                final var keyStart = current;
                final var colonIndex = findFlowDelimiter(text, keyStart, ':');
                if (colonIndex < 0) {
                    throw new IllegalArgumentException("Expected YAML mapping entry");
                }
                final var keyText = text.substring(keyStart, colonIndex).stripTrailing();
                final var key = parseKeyToken(keyText);
                final var keyPath = new ArrayList<>(path);
                keyPath.add(key);
                final var serializedPath = serializePath(keyPath);
                if (locations.containsKey(serializedPath) || value.containsKey(key)) {
                    throw new IllegalArgumentException("Duplicate YAML key");
                }
                locations.put(serializedPath, Map.of("row", row, "col", baseColumn + keyStart));

                current = skipFlowWhitespace(text, colonIndex + 1);
                final var parsed = parseFlowNode(text, current, row, baseColumn, keyPath, locations);
                value.put(key, parsed.value());
                current = skipFlowWhitespace(text, parsed.nextIndex());
                if (current < text.length() && text.charAt(current) == ',') {
                    current = skipFlowWhitespace(text, current + 1);
                    continue;
                }
                if (current < text.length() && text.charAt(current) == '}') {
                    return new FlowNode(value, current + 1);
                }
                break;
            }
            throw new IllegalArgumentException("Invalid YAML flow collection");
        }

        final var endIndex = findFlowScalarEnd(text, index);
        return new FlowNode(parseScalar(text.substring(index, endIndex).strip()), endIndex);
    }

    private static InlineEntry parseInlineEntry(String text, int baseColumn) {
        final var leadingSpaces = text.length() - text.stripLeading().length();
        final var trimmed = text.stripLeading();
        final var colonIndex = findMappingColon(trimmed);
        if (colonIndex < 0) {
            throw new IllegalArgumentException("Expected YAML mapping entry");
        }
        final var keyText = trimmed.substring(0, colonIndex).stripTrailing();
        final var remainder = trimmed.substring(colonIndex + 1);
        final var valueText = remainder.stripLeading();
        final var spacesBeforeValue = remainder.length() - valueText.length();
        return new InlineEntry(
                parseKeyToken(keyText),
                baseColumn + leadingSpaces,
                valueText,
                baseColumn + leadingSpaces + colonIndex + 1 + spacesBeforeValue);
    }

    private static String parseKeyToken(String text) {
        final var trimmed = text.strip();
        if ((trimmed.startsWith("\"") && trimmed.endsWith("\"")) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
            return decodeQuotedString(trimmed);
        }
        if (trimmed.equals("///") || trimmed.equals("->")) {
            return trimmed;
        }
        if (!trimmed.matches("^[A-Za-z][A-Za-z0-9_.!]*$")) {
            throw new IllegalArgumentException("Invalid YAML key");
        }
        return trimmed;
    }

    private static String decodeQuotedString(String text) {
        try {
            if (text.startsWith("\"")) {
                return OBJECT_MAPPER.readValue(text, String.class);
            }
        } catch (Exception e) {
            throw new IllegalArgumentException(e);
        }

        final var builder = new StringBuilder();
        for (int index = 1; index < text.length() - 1; index += 1) {
            if (text.charAt(index) == '\'' && index + 1 < text.length() - 1 && text.charAt(index + 1) == '\'') {
                builder.append('\'');
                index += 1;
                continue;
            }
            builder.append(text.charAt(index));
        }
        return builder.toString();
    }

    private static Object parseScalar(String text) {
        return switch (text) {
            case "null" -> null;
            case "true" -> true;
            case "false" -> false;
            default -> {
                if (text.matches("^-?(0|[1-9][0-9]*)$")) {
                    yield Integer.parseInt(text);
                }
                if (text.matches("^-?(0|[1-9][0-9]*)\\.[0-9]+$")) {
                    yield Double.parseDouble(text);
                }
                if ((text.startsWith("\"") && text.endsWith("\"")) || (text.startsWith("'") && text.endsWith("'"))) {
                    yield decodeQuotedString(text);
                }
                yield text;
            }
        };
    }

    private static int findMappingColon(String text) {
        Character quote = null;
        for (int index = 0; index < text.length(); index += 1) {
            final var c = text.charAt(index);
            if (c == '"' || c == '\'') {
                quote = quote != null && quote == c ? null : (quote == null ? c : quote);
                continue;
            }
            if (quote == null && c == ':' && (index + 1 == text.length() || text.charAt(index + 1) == ' ')) {
                return index;
            }
        }
        return -1;
    }

    private static void rejectUnsupportedYaml(String line) {
        final var trimmed = trimComment(line).strip();
        if (trimmed.isEmpty()) {
            return;
        }
        if (trimmed.equals("---") || trimmed.equals("...")) {
            throw new IllegalArgumentException("YAML multi-document markers are not supported");
        }
        if (Pattern.compile("^\\s*[&*]").matcher(line).find()
                || Pattern.compile(":\\s*[&*]").matcher(line).find()
                || Pattern.compile("-\\s*[&*]").matcher(line).find()) {
            throw new IllegalArgumentException("YAML anchors and aliases are not supported");
        }
        if (Pattern.compile("^\\s*!").matcher(line).find()
                || Pattern.compile(":\\s*!").matcher(line).find()
                || Pattern.compile("-\\s*!").matcher(line).find()) {
            throw new IllegalArgumentException("YAML tags are not supported");
        }
        if (trimmed.contains("<<:")) {
            throw new IllegalArgumentException("YAML merge keys are not supported");
        }
    }

    private static String trimComment(String text) {
        Character quote = null;
        for (int index = 0; index < text.length(); index += 1) {
            final var c = text.charAt(index);
            if (c == '"' || c == '\'') {
                quote = quote != null && quote == c ? null : (quote == null ? c : quote);
                continue;
            }
            if (quote == null && c == '#') {
                return text.substring(0, index).stripTrailing();
            }
        }
        return text.stripTrailing();
    }

    private static LineInfo getLineInfo(String[] lines, int index) {
        final var content = trimComment(lines[index]);
        return new LineInfo(index, countIndent(lines[index]), content, content.strip());
    }

    private static LineInfo peekSignificantLine(String[] lines, int startIndex) {
        for (int index = startIndex; index < lines.length; index += 1) {
            final var info = getLineInfo(lines, index);
            if (!info.trimmed().isEmpty()) {
                return info;
            }
        }
        return null;
    }

    private static int countIndent(String line) {
        var indent = 0;
        while (indent < line.length() && line.charAt(indent) == ' ') {
            indent += 1;
        }
        return indent;
    }

    private static String serializePath(List<Object> path) {
        try {
            return OBJECT_MAPPER.writeValueAsString(path);
        } catch (Exception e) {
            throw new IllegalArgumentException(e);
        }
    }
}
