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

package schema

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

type yamlLineInfo struct {
	Index   int
	Indent  int
	Content string
	Trimmed string
}

type yamlNode struct {
	Value     any
	NextIndex int
}

func CreatePathDocumentYAMLCoordinatesPseudoJSONLocator(text string) (DocumentLocator, error) {
	normalized := strings.ReplaceAll(strings.ReplaceAll(text, "\r\n", "\n"), "\r", "\n")
	lines := strings.Split(normalized, "\n")
	for _, line := range lines {
		if strings.HasPrefix(line, " \t") || strings.HasPrefix(line, "\t") {
			return nil, fmt.Errorf("tabs are not supported in Telepact YAML")
		}
		if err := rejectUnsupportedYAML(line); err != nil {
			return nil, err
		}
	}

	firstInfo := peekSignificantYAMLLine(lines, 0)
	if firstInfo == nil || firstInfo.Indent != 0 {
		return nil, fmt.Errorf("Telepact YAML must start at the root sequence")
	}

	locations := make(map[string]map[string]any)
	parsed, err := parseYAMLNode(lines, firstInfo.Index, 0, nil, locations)
	if err != nil {
		return nil, err
	}

	if _, ok := parsed.Value.([]any); !ok {
		return nil, fmt.Errorf("Telepact YAML root must be a sequence")
	}

	locator := func(path []any) map[string]any {
		key := serializeYAMLPath(path)
		if location, ok := locations[key]; ok {
			return location
		}
		return map[string]any{"row": 1, "col": 1}
	}

	return locator, nil
}

func GetPathDocumentYAMLCoordinatesPseudoJSON(path []any, document string) map[string]any {
	locator, err := CreatePathDocumentYAMLCoordinatesPseudoJSONLocator(document)
	if err != nil {
		return defaultDocumentCoordinates()
	}
	return locator(path)
}

func parseYAMLNode(lines []string, startIndex int, indent int, path []any, locations map[string]map[string]any) (*yamlNode, error) {
	info := peekSignificantYAMLLine(lines, startIndex)
	if info == nil {
		return nil, fmt.Errorf("unexpected end of YAML document")
	}
	if info.Indent != indent {
		return nil, fmt.Errorf("unexpected YAML indentation")
	}
	if info.Trimmed == "-" || strings.HasPrefix(info.Trimmed, "- ") {
		return parseYAMLSequence(lines, startIndex, indent, path, locations)
	}
	return parseYAMLMapEntries(lines, startIndex, indent, path, locations, nil)
}

func parseYAMLSequence(lines []string, startIndex int, indent int, path []any, locations map[string]map[string]any) (*yamlNode, error) {
	value := make([]any, 0)
	lineIndex := startIndex

	for {
		info := peekSignificantYAMLLine(lines, lineIndex)
		if info == nil || info.Indent < indent {
			break
		}
		if info.Indent != indent || !(info.Trimmed == "-" || strings.HasPrefix(info.Trimmed, "- ")) {
			break
		}

		itemPath := append(append([]any{}, path...), len(value))
		locations[serializeYAMLPath(itemPath)] = map[string]any{"row": info.Index + 1, "col": indent + 1}

		afterDash := info.Content[indent+1:]
		valueText := strings.TrimLeft(afterDash, " ")
		if valueText == "" {
			nextInfo := peekSignificantYAMLLine(lines, info.Index+1)
			if nextInfo == nil || nextInfo.Indent <= indent {
				value = append(value, nil)
				lineIndex = info.Index + 1
				continue
			}
			parsed, err := parseYAMLNode(lines, nextInfo.Index, nextInfo.Indent, itemPath, locations)
			if err != nil {
				return nil, err
			}
			value = append(value, parsed.Value)
			lineIndex = parsed.NextIndex
			continue
		}

		valueColumn := indent + 2 + (len(afterDash) - len(valueText))
		if !startsYAMLFlowCollection(valueText) && findYAMLMappingColon(valueText) >= 0 {
			parsed, err := parseYAMLMapEntries(lines, info.Index+1, indent+2, itemPath, locations, map[string]any{
				"info":        info,
				"text":        afterDash,
				"base_column": indent + 2,
			})
			if err != nil {
				return nil, err
			}
			value = append(value, parsed.Value)
			lineIndex = parsed.NextIndex
			continue
		}

		parsedValue, err := parseYAMLValueText(lines, info, indent, itemPath, valueText, valueColumn, locations)
		if err != nil {
			return nil, err
		}
		value = append(value, parsedValue.Value)
		lineIndex = parsedValue.NextIndex
	}

	return &yamlNode{Value: value, NextIndex: lineIndex}, nil
}

func parseYAMLMapEntries(lines []string, startIndex int, indent int, path []any, locations map[string]map[string]any, initialEntry map[string]any) (*yamlNode, error) {
	value := make(map[string]any)
	lineIndex := startIndex
	firstEntry := initialEntry

	for {
		var info *yamlLineInfo
		if firstEntry != nil {
			info = firstEntry["info"].(*yamlLineInfo)
		} else {
			info = peekSignificantYAMLLine(lines, lineIndex)
		}
		if info == nil {
			break
		}
		if firstEntry == nil && info.Indent < indent {
			break
		}
		if firstEntry == nil && (info.Indent != indent || strings.HasPrefix(info.Trimmed, "-")) {
			if firstEntry != nil {
				return nil, fmt.Errorf("unexpected YAML mapping indentation")
			}
			break
		}

		entryText := info.Content[indent:]
		baseColumn := indent + 1
		if firstEntry != nil {
			entryText = firstEntry["text"].(string)
			baseColumn = firstEntry["base_column"].(int)
		}

		entry, err := parseYAMLInlineEntry(entryText, baseColumn)
		if err != nil {
			return nil, err
		}
		key := entry["key"].(string)
		keyPath := append(append([]any{}, path...), key)
		serializedPath := serializeYAMLPath(keyPath)
		if _, exists := locations[serializedPath]; exists {
			return nil, fmt.Errorf("duplicate YAML key")
		}
		if _, exists := value[key]; exists {
			return nil, fmt.Errorf("duplicate YAML key")
		}
		locations[serializedPath] = map[string]any{"row": info.Index + 1, "col": entry["key_column"].(int)}

		parsedValue, err := parseYAMLValueText(lines, info, indent, keyPath, entry["value_text"].(string), entry["value_column"].(int), locations)
		if err != nil {
			return nil, err
		}
		value[key] = parsedValue.Value
		lineIndex = parsedValue.NextIndex
		firstEntry = nil
	}

	return &yamlNode{Value: value, NextIndex: lineIndex}, nil
}

func parseYAMLValueText(lines []string, info *yamlLineInfo, currentIndent int, path []any, valueText string, valueColumn int, locations map[string]map[string]any) (*yamlNode, error) {
	switch valueText {
	case "{}":
		return &yamlNode{Value: map[string]any{}, NextIndex: info.Index + 1}, nil
	case "[]":
		return &yamlNode{Value: []any{}, NextIndex: info.Index + 1}, nil
	case "|":
		return parseYAMLBlockScalar(lines, info.Index+1, currentIndent, false)
	case ">":
		return parseYAMLBlockScalar(lines, info.Index+1, currentIndent, true)
	case "":
		nextInfo := peekSignificantYAMLLine(lines, info.Index+1)
		if nextInfo == nil || nextInfo.Indent <= currentIndent {
			return &yamlNode{Value: nil, NextIndex: info.Index + 1}, nil
		}
		return parseYAMLNode(lines, nextInfo.Index, nextInfo.Indent, path, locations)
	default:
		if startsYAMLFlowCollection(valueText) {
			parsed, err := parseYAMLFlowNode(valueText, 0, info.Index+1, valueColumn, path, locations)
			if err != nil {
				return nil, err
			}
			if skipYAMLFlowWhitespace(valueText, parsed.NextIndex) != len(valueText) {
				return nil, fmt.Errorf("invalid YAML flow collection")
			}
			return &yamlNode{Value: parsed.Value, NextIndex: info.Index + 1}, nil
		}
		return &yamlNode{Value: parseYAMLScalar(valueText), NextIndex: info.Index + 1}, nil
	}
}

func parseYAMLBlockScalar(lines []string, startIndex int, parentIndent int, folded bool) (*yamlNode, error) {
	index := startIndex
	blockLines := make([]string, 0)
	minIndent := -1

	for index < len(lines) {
		info := getYAMLLineInfo(lines, index)
		if info.Trimmed != "" && info.Indent <= parentIndent {
			break
		}
		if info.Trimmed != "" && (minIndent == -1 || info.Indent < minIndent) {
			minIndent = info.Indent
		}
		blockLines = append(blockLines, lines[index])
		index++
	}

	contentIndent := parentIndent + 1
	if minIndent >= 0 {
		contentIndent = minIndent
	}

	normalizedLines := make([]string, 0, len(blockLines))
	for _, line := range blockLines {
		if strings.TrimSpace(trimYAMLComment(line)) == "" {
			normalizedLines = append(normalizedLines, "")
			continue
		}
		if contentIndent < len(line) {
			normalizedLines = append(normalizedLines, line[contentIndent:])
		} else {
			normalizedLines = append(normalizedLines, "")
		}
	}

	if !folded {
		return &yamlNode{Value: strings.Join(normalizedLines, "\n"), NextIndex: index}, nil
	}

	var builder strings.Builder
	for _, line := range normalizedLines {
		if line == "" {
			builder.WriteString("\n")
			continue
		}
		if builder.Len() > 0 && !strings.HasSuffix(builder.String(), "\n") {
			builder.WriteString(" ")
		}
		builder.WriteString(line)
	}
	return &yamlNode{Value: builder.String(), NextIndex: index}, nil
}

func trimYAMLComment(text string) string {
	quote := rune(0)
	for index, char := range text {
		if char == '"' || char == '\'' {
			if quote == char {
				quote = 0
			} else if quote == 0 {
				quote = char
			}
			continue
		}
		if quote == 0 && char == '#' {
			return strings.TrimRight(text[:index], " ")
		}
	}
	return strings.TrimRight(text, " ")
}

func getYAMLLineInfo(lines []string, index int) *yamlLineInfo {
	content := trimYAMLComment(lines[index])
	return &yamlLineInfo{
		Index:   index,
		Indent:  countYAMLIndent(lines[index]),
		Content: content,
		Trimmed: strings.TrimSpace(content),
	}
}

func peekSignificantYAMLLine(lines []string, startIndex int) *yamlLineInfo {
	for index := startIndex; index < len(lines); index++ {
		info := getYAMLLineInfo(lines, index)
		if info.Trimmed != "" {
			return info
		}
	}
	return nil
}

func countYAMLIndent(line string) int {
	indent := 0
	for indent < len(line) && line[indent] == ' ' {
		indent++
	}
	return indent
}

func rejectUnsupportedYAML(line string) error {
	trimmed := strings.TrimSpace(trimYAMLComment(line))
	if trimmed == "" {
		return nil
	}
	if trimmed == "---" || trimmed == "..." {
		return fmt.Errorf("YAML multi-document markers are not supported")
	}
	if regexp.MustCompile(`^\s*[&*]`).MatchString(line) || regexp.MustCompile(`:\s*[&*]`).MatchString(line) || regexp.MustCompile(`-\s*[&*]`).MatchString(line) {
		return fmt.Errorf("YAML anchors and aliases are not supported")
	}
	if regexp.MustCompile(`^\s*!`).MatchString(line) || regexp.MustCompile(`:\s*!`).MatchString(line) || regexp.MustCompile(`-\s*!`).MatchString(line) {
		return fmt.Errorf("YAML tags are not supported")
	}
	if strings.Contains(trimmed, "<<:") {
		return fmt.Errorf("YAML merge keys are not supported")
	}
	return nil
}

func parseYAMLInlineEntry(text string, baseColumn int) (map[string]any, error) {
	leadingSpaces := len(text) - len(strings.TrimLeft(text, " "))
	trimmed := strings.TrimLeft(text, " ")
	colonIndex := findYAMLMappingColon(trimmed)
	if colonIndex < 0 {
		return nil, fmt.Errorf("expected YAML mapping entry")
	}
	keyText := strings.TrimRight(trimmed[:colonIndex], " ")
	remainder := trimmed[colonIndex+1:]
	valueText := strings.TrimLeft(remainder, " ")
	spacesBeforeValue := len(remainder) - len(valueText)
	key, err := parseYAMLKeyToken(keyText)
	if err != nil {
		return nil, err
	}
	return map[string]any{
		"key":          key,
		"key_column":   baseColumn + leadingSpaces,
		"value_text":   valueText,
		"value_column": baseColumn + leadingSpaces + colonIndex + 1 + spacesBeforeValue,
	}, nil
}

func startsYAMLFlowCollection(text string) bool {
	return strings.HasPrefix(text, "{") || strings.HasPrefix(text, "[")
}

func skipYAMLFlowWhitespace(text string, index int) int {
	current := index
	for current < len(text) && text[current] == ' ' {
		current++
	}
	return current
}

func findYAMLFlowDelimiter(text string, startIndex int, delimiter rune) int {
	quote := rune(0)
	for index, char := range text[startIndex:] {
		actual := startIndex + index
		if char == '"' || char == '\'' {
			if quote == char {
				quote = 0
			} else if quote == 0 {
				quote = char
			}
			continue
		}
		if quote == 0 && char == delimiter {
			return actual
		}
	}
	return -1
}

func findYAMLFlowScalarEnd(text string, startIndex int) int {
	quote := rune(0)
	for index, char := range text[startIndex:] {
		actual := startIndex + index
		if char == '"' || char == '\'' {
			if quote == char {
				quote = 0
			} else if quote == 0 {
				quote = char
			}
			continue
		}
		if quote == 0 && (char == ',' || char == ']' || char == '}') {
			return actual
		}
	}
	return len(text)
}

func parseYAMLFlowNode(text string, startIndex int, row int, baseColumn int, path []any, locations map[string]map[string]any) (*yamlNode, error) {
	index := skipYAMLFlowWhitespace(text, startIndex)
	if index >= len(text) {
		return nil, fmt.Errorf("unexpected end of YAML flow collection")
	}

	switch text[index] {
	case '[':
		value := make([]any, 0)
		current := skipYAMLFlowWhitespace(text, index+1)
		if current < len(text) && text[current] == ']' {
			return &yamlNode{Value: value, NextIndex: current + 1}, nil
		}

		for current < len(text) {
			itemPath := append(append([]any{}, path...), len(value))
			locations[serializeYAMLPath(itemPath)] = map[string]any{"row": row, "col": baseColumn + current}
			parsed, err := parseYAMLFlowNode(text, current, row, baseColumn, itemPath, locations)
			if err != nil {
				return nil, err
			}
			value = append(value, parsed.Value)
			current = skipYAMLFlowWhitespace(text, parsed.NextIndex)
			if current < len(text) && text[current] == ',' {
				current = skipYAMLFlowWhitespace(text, current+1)
				continue
			}
			if current < len(text) && text[current] == ']' {
				return &yamlNode{Value: value, NextIndex: current + 1}, nil
			}
			break
		}
		return nil, fmt.Errorf("invalid YAML flow collection")
	case '{':
		value := make(map[string]any)
		current := skipYAMLFlowWhitespace(text, index+1)
		if current < len(text) && text[current] == '}' {
			return &yamlNode{Value: value, NextIndex: current + 1}, nil
		}

		for current < len(text) {
			keyStart := current
			colonIndex := findYAMLFlowDelimiter(text, keyStart, ':')
			if colonIndex < 0 {
				return nil, fmt.Errorf("expected YAML mapping entry")
			}
			keyText := strings.TrimRight(text[keyStart:colonIndex], " ")
			key, err := parseYAMLKeyToken(keyText)
			if err != nil {
				return nil, err
			}
			keyPath := append(append([]any{}, path...), key)
			serializedPath := serializeYAMLPath(keyPath)
			if _, exists := locations[serializedPath]; exists {
				return nil, fmt.Errorf("duplicate YAML key")
			}
			if _, exists := value[key]; exists {
				return nil, fmt.Errorf("duplicate YAML key")
			}
			locations[serializedPath] = map[string]any{"row": row, "col": baseColumn + keyStart}

			current = skipYAMLFlowWhitespace(text, colonIndex+1)
			parsed, err := parseYAMLFlowNode(text, current, row, baseColumn, keyPath, locations)
			if err != nil {
				return nil, err
			}
			value[key] = parsed.Value
			current = skipYAMLFlowWhitespace(text, parsed.NextIndex)
			if current < len(text) && text[current] == ',' {
				current = skipYAMLFlowWhitespace(text, current+1)
				continue
			}
			if current < len(text) && text[current] == '}' {
				return &yamlNode{Value: value, NextIndex: current + 1}, nil
			}
			break
		}
		return nil, fmt.Errorf("invalid YAML flow collection")
	default:
		endIndex := findYAMLFlowScalarEnd(text, index)
		return &yamlNode{Value: parseYAMLScalar(strings.TrimSpace(text[index:endIndex])), NextIndex: endIndex}, nil
	}
}

func parseYAMLKeyToken(text string) (string, error) {
	trimmed := strings.TrimSpace(text)
	if (strings.HasPrefix(trimmed, `"`) && strings.HasSuffix(trimmed, `"`)) || (strings.HasPrefix(trimmed, `'`) && strings.HasSuffix(trimmed, `'`)) {
		return decodeYAMLQuotedString(trimmed)
	}
	if trimmed == "///" || trimmed == "->" {
		return trimmed, nil
	}
	if !regexp.MustCompile(`^[A-Za-z][A-Za-z0-9_.!]*$`).MatchString(trimmed) {
		return "", fmt.Errorf("invalid YAML key")
	}
	return trimmed, nil
}

func decodeYAMLQuotedString(text string) (string, error) {
	if strings.HasPrefix(text, `"`) {
		var value string
		if err := json.Unmarshal([]byte(text), &value); err != nil {
			return "", err
		}
		return value, nil
	}

	var builder strings.Builder
	for index := 1; index < len(text)-1; index++ {
		if text[index] == '\'' && index+1 < len(text)-1 && text[index+1] == '\'' {
			builder.WriteByte('\'')
			index++
			continue
		}
		builder.WriteByte(text[index])
	}
	return builder.String(), nil
}

func parseYAMLScalar(text string) any {
	switch text {
	case "null":
		return nil
	case "true":
		return true
	case "false":
		return false
	}
	if matched, _ := regexp.MatchString(`^-?(0|[1-9][0-9]*)$`, text); matched {
		if value, err := strconv.Atoi(text); err == nil {
			return value
		}
	}
	if matched, _ := regexp.MatchString(`^-?(0|[1-9][0-9]*)\.[0-9]+$`, text); matched {
		if value, err := strconv.ParseFloat(text, 64); err == nil {
			return value
		}
	}
	if (strings.HasPrefix(text, `"`) && strings.HasSuffix(text, `"`)) || (strings.HasPrefix(text, `'`) && strings.HasSuffix(text, `'`)) {
		if value, err := decodeYAMLQuotedString(text); err == nil {
			return value
		}
	}
	return text
}

func findYAMLMappingColon(text string) int {
	quote := rune(0)
	for index, char := range text {
		if char == '"' || char == '\'' {
			if quote == char {
				quote = 0
			} else if quote == 0 {
				quote = char
			}
			continue
		}
		if quote == 0 && char == ':' {
			if index+1 == len(text) || text[index+1] == ' ' {
				return index
			}
		}
	}
	return -1
}

func serializeYAMLPath(path []any) string {
	bytes, _ := json.Marshal(path)
	return string(bytes)
}
