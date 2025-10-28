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

import "strings"

// GetPathDocumentCoordinatesPseudoJSON locates the row/column coordinates in the document for the given path.
func GetPathDocumentCoordinatesPseudoJSON(path []any, document string) map[string]any {
	reader := newRuneReader(document)
	return findCoordinates(path, reader, nil, nil)
}

type runeReader struct {
	runes []rune
	index int
	row   int
	col   int
}

func newRuneReader(document string) *runeReader {
	return &runeReader{
		runes: []rune(document),
		row:   1,
		col:   0,
	}
}

func (r *runeReader) next() (rune, int, int, bool) {
	if r.index >= len(r.runes) {
		return 0, r.row, r.col, false
	}

	ch := r.runes[r.index]
	r.index++

	if ch == '\n' {
		r.row++
		r.col = 0
	} else {
		r.col++
	}

	return ch, r.row, r.col, true
}

func findCoordinates(path []any, reader *runeReader, overrideRow, overrideCol *int) map[string]any {
	for {
		ch, row, col, ok := reader.next()
		if !ok {
			break
		}

		if len(path) == 0 {
			targetRow := row
			if overrideRow != nil {
				targetRow = *overrideRow
			}
			targetCol := col
			if overrideCol != nil {
				targetCol = *overrideCol
			}
			return map[string]any{"row": targetRow, "col": targetCol}
		}

		switch ch {
		case '{':
			if result := findCoordinatesObject(path, reader); result != nil {
				return result
			}
		case '[':
			if result := findCoordinatesArray(path, reader); result != nil {
				return result
			}
		}
	}

	panic("path not found in document")
}

func findCoordinatesObject(path []any, reader *runeReader) map[string]any {
	var workingKey string
	var keyRow, keyCol int
	var hasKey bool

	for {
		ch, row, col, ok := reader.next()
		if !ok {
			break
		}

		switch ch {
		case '}':
			return nil
		case ' ': // skip whitespace
			continue
		case '\n', '\r', '\t':
			continue
		case ',':
			hasKey = false
		case '"':
			keyRow = row
			keyCol = col
			workingKey = findString(reader)
			hasKey = true
		case ':':
			if !hasKey || len(path) == 0 {
				continue
			}
			key, ok := path[0].(string)
			if !ok {
				continue
			}
			if key == workingKey {
				return findCoordinates(path[1:], reader, &keyRow, &keyCol)
			}
			findValue(reader)
			hasKey = false
		default:
			continue
		}
	}

	panic("object path not found")
}

func findCoordinatesArray(path []any, reader *runeReader) map[string]any {
	if len(path) == 0 {
		return findCoordinates(path, reader, nil, nil)
	}

	targetIndex, ok := toInt(path[0])
	if !ok {
		return nil
	}

	workingIndex := 0
	if workingIndex == targetIndex {
		return findCoordinates(path[1:], reader, nil, nil)
	}
	findValue(reader)

	for {
		ch, _, _, ok := reader.next()
		if !ok {
			break
		}
		switch ch {
		case ']':
			return nil
		case ',':
			workingIndex++
			if workingIndex == targetIndex {
				return findCoordinates(path[1:], reader, nil, nil)
			}
			findValue(reader)
		case ' ', '\n', '\r', '\t':
			continue
		default:
			continue
		}
	}

	panic("array path not found")
}

func findValue(reader *runeReader) bool {
	for {
		ch, _, _, ok := reader.next()
		if !ok {
			break
		}
		switch ch {
		case '{':
			findObject(reader)
			return false
		case '[':
			findArray(reader)
			return false
		case '"':
			findString(reader)
			return false
		case '}':
			return true
		case ']':
			return true
		case ',':
			return false
		case ' ', '\n', '\r', '\t':
			continue
		default:
			// continue scanning primitive tokens
			continue
		}
	}

	panic("value not found in document")
}

func findObject(reader *runeReader) {
	for {
		ch, _, _, ok := reader.next()
		if !ok {
			break
		}
		switch ch {
		case '}':
			return
		case '"':
			findString(reader)
		case ':':
			if findValue(reader) {
				return
			}
		}
	}

	panic("object not terminated in document")
}

func findArray(reader *runeReader) {
	if findValue(reader) {
		return
	}

	for {
		ch, _, _, ok := reader.next()
		if !ok {
			break
		}
		switch ch {
		case ']':
			return
		case ',':
			if findValue(reader) {
				return
			}
		case ' ', '\n', '\r', '\t':
			continue
		default:
			continue
		}
	}

	panic("array not terminated in document")
}

func findString(reader *runeReader) string {
	var builder strings.Builder
	for {
		ch, _, _, ok := reader.next()
		if !ok {
			break
		}
		if ch == '"' {
			return builder.String()
		}
		builder.WriteRune(ch)
	}

	panic("string not closed in document")
}

func toInt(value any) (int, bool) {
	switch v := value.(type) {
	case int:
		return v, true
	case int8:
		return int(v), true
	case int16:
		return int(v), true
	case int32:
		return int(v), true
	case int64:
		return int(v), true
	case uint:
		return int(v), true
	case uint8:
		return int(v), true
	case uint16:
		return int(v), true
	case uint32:
		return int(v), true
	case uint64:
		return int(v), true
	case float64:
		return int(v), true
	case float32:
		return int(v), true
	default:
		return 0, false
	}
}
