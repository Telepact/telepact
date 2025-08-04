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

import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class GetPathDocumentCoordinatesPseudoJson {

    public static Map<String, Object> getPathDocumentCoordinatesPseudoJson(List<Object> path, String document) {
        System.out.println("getPathDocumentCoordinatesPseudoJson: path=" + path + ", document=" + document);

        Iterator<CharacterPosition> reader = stringReader(document);
        return findCoordinates(path, reader, null, null);
    }

    private static Iterator<CharacterPosition> stringReader(String s) {
        return new Iterator<CharacterPosition>() {
            private int row = 1;
            private int col = 0;
            private int index = 0;

            @Override
            public boolean hasNext() {
                return index < s.length();
            }

            @Override
            public CharacterPosition next() {
                char c = s.charAt(index++);
                if (c == '\n') {
                    row++;
                    col = 0;
                } else {
                    col++;
                }
                return new CharacterPosition(c, row, col);
            }
        };
    }

    private static Map<String, Object> findCoordinates(List<Object> path, Iterator<CharacterPosition> reader,
            Integer ovRow, Integer ovCol) {

        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            if (path.isEmpty()) {
                return Map.of(
                        "row", ovRow != null ? ovRow : row,
                        "col", ovCol != null ? ovCol : col);
            }

            if (c == '{') {
                Map<String, Object> result = findCoordinatesObject(path, reader);
                if (result != null) {
                    return result;
                }
            }
            if (c == '[') {
                Map<String, Object> result = findCoordinatesArray(path, reader);
                if (result != null) {
                    return result;
                }
            }
        }

        throw new IllegalArgumentException("Path not found in document");
    }

    private static Map<String, Object> findCoordinatesObject(List<Object> path, Iterator<CharacterPosition> reader) {
        Integer workingKeyRowStart = null;
        Integer workingKeyColStart = null;
        String workingKey = null;

        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            //System.out.println("findCoordinatesObject: char=" + c + ", row=" + row + ", col=" + col);
            if (c == '}') {
                return null;
            } else if (c == '"') {
                workingKeyRowStart = row;
                workingKeyColStart = col;
                workingKey = findString(reader);
            } else if (c == ':') {
                if (workingKey.equals(path.get(0))) {
                    return findCoordinates(path.subList(1, path.size()), reader, workingKeyRowStart,
                            workingKeyColStart);
                } else {
                    findValue(reader);
                }
            }
        }

        throw new IllegalArgumentException("Path not found in document");
    }

    private static Map<String, Object> findCoordinatesArray(List<Object> path, Iterator<CharacterPosition> reader) {
        int workingIndex = 0;

        if (workingIndex == (int) path.get(0)) {
            return findCoordinates(path.subList(1, path.size()), reader, null, null);
        } else {
            findValue(reader);
        }

        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            //System.out.println("findCoordinatesArray: char=" + c + ", row=" + row + ", col=" + col);
            workingIndex++;
            if (workingIndex == (int) path.get(0)) {
                return findCoordinates(path.subList(1, path.size()), reader, null, null);
            } else {
                findValue(reader);
            }
        }

        throw new IllegalArgumentException("Path not found in document");
    }

    private static boolean findValue(Iterator<CharacterPosition> reader) {
        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            //System.out.println("findValue: char=" + c + ", row=" + row + ", col=" + col);
            if (c == '{') {
                findObject(reader);
                return false;
            } else if (c == '[') {
                findArray(reader);
                return false;
            } else if (c == '"') {
                findString(reader);
                return false;
            } else if (c == '}') {
                return true;
            } else if (c == ']') {
                return true;
            } else if (c == ',') {
                return false;
            }
        }

        throw new IllegalArgumentException("Value not found in document");
    }

    private static void findObject(Iterator<CharacterPosition> reader) {
        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            //System.out.println("findObject: char=" + c + ", row=" + row + ", col=" + col);
            if (c == '}') {
                return;
            } else if (c == '"') {
                findString(reader);
            } else if (c == ':') {
                if (findValue(reader)) {
                    return;
                }
            }
        }
    }

    private static void findArray(Iterator<CharacterPosition> reader) {
        if (findValue(reader)) {
            return;
        }

        int workingIndex = 0;
        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;
            int row = cp.row;
            int col = cp.col;

            //System.out.println("findArray: char=" + c + ", row=" + row + ", col=" + col);
            if (c == ']') {
                return;
            }
            workingIndex++;
            if (findValue(reader)) {
                return;
            }
        }
    }

    private static String findString(Iterator<CharacterPosition> reader) {
        StringBuilder workingString = new StringBuilder();
        while (reader.hasNext()) {
            CharacterPosition cp = reader.next();
            char c = cp.character;

            //System.out.println("findString: char=" + c);
            if (c == '"') {
                return workingString.toString();
            } else {
                workingString.append(c);
            }
        }

        throw new IllegalArgumentException("String not closed");
    }

    private static class CharacterPosition {
        public final char character;
        public final int row;
        public final int col;

        public CharacterPosition(char character, int row, int col) {
            this.character = character;
            this.row = row;
            this.col = col;
        }
    }
}
