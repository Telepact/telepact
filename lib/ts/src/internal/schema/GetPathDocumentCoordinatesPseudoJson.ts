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

type Path = (string | number)[];
type Coordinates = { row: number; col: number };

class StringReader {
    private s: string;
    private index: number;
    private row: number;
    private col: number;

    constructor(s: string) {
        this.s = s;
        this.index = 0;
        this.row = 1;
        this.col = 0;
    }

    next(): [string, number, number] | null {
        if (this.index >= this.s.length) {
            return null;
        }
        const c = this.s[this.index++];
        if (c === '\n') {
            this.row += 1;
            this.col = 0;
        } else {
            this.col += 1;
        }
        //console.log(`reader: char=${c}, row=${this.row}, col=${this.col}`);
        return [c, this.row, this.col];
    }
}

export function getPathDocumentCoordinatesPseudoJson(path: Path, document: string): Coordinates {
    //console.log(`getPathDocumentCoordinatesPseudoJson: path=${path}, document=${document}`);
    const reader = new StringReader(document);
    return findCoordinates(path, reader);
}

function findCoordinates(path: Path, reader: StringReader, ovRow?: number, ovCol?: number): Coordinates {
    //console.log(`findCoordinates: path=${path}`);

    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        if (path.length === 0) {
            return {
                row: ovRow ?? row,
                col: ovCol ?? col,
            };
        }

        //console.log(`findCoordinates: char=${c}, row=${row}, col=${col}`);
        if (c === '{') {
            const result = findCoordinatesObject(path, reader);
            if (result) {
                return result;
            }
        }
        if (c === '[') {
            const result = findCoordinatesArray(path, reader);
            if (result) {
                return result;
            }
        }
    }

    throw new Error('findCoordinates: Path not found in document');
}

function findCoordinatesObject(path: Path, reader: StringReader): Coordinates | null {
    //console.log(`findCoordinatesObject: path=${path}`);
    let workingKeyRowStart: number | null = null;
    let workingKeyColStart: number | null = null;
    let workingKey: string | undefined;

    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findCoordinatesObject: char=${c}, row=${row}, col=${col}`);
        if (c === '}') {
            return null;
        } else if (c === '"') {
            workingKeyRowStart = row;
            workingKeyColStart = col;
            workingKey = findString(reader);
        } else if (c === ':') {
            if (workingKey === path[0]) {
                return findCoordinates(path.slice(1), reader, workingKeyRowStart, workingKeyColStart);
            } else {
                findValue(reader);
            }
        }
    }

    throw new Error('findCoordinatesObject: Path not found in document');
}

function findCoordinatesArray(path: Path, reader: StringReader): Coordinates | null {
    //console.log(`findCoordinatesArray: path=${path}`);
    let workingIndex = 0;

    if (workingIndex === path[0]) {
        return findCoordinates(path.slice(1), reader);
    } else {
        findValue(reader);
    }

    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findCoordinatesArray: char=${c}, row=${row}, col=${col}`);
        workingIndex += 1;
        //console.log(`findCoordinatesArray: workingIndex=${workingIndex}`);
        if (workingIndex === path[0]) {
            return findCoordinates(path.slice(1), reader);
        } else {
            findValue(reader);
        }
    }

    throw new Error('findCoordinatesArray: Path not found in document');
}

function findValue(reader: StringReader): boolean {
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findValue: char=${c}, row=${row}, col=${col}`);
        if (c === '{') {
            findObject(reader);
            return false;
        } else if (c === '[') {
            findArray(reader);
            return false;
        } else if (c === '"') {
            findString(reader);
            return false;
        } else if (c === '}') {
            return true;
        } else if (c === ']') {
            return true;
        } else if (c === ',') {
            return false;
        }
    }
    throw new Error('Value not found in document');
}

function findObject(reader: StringReader): void {
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findObject: char=${c}, row=${row}, col=${col}`);
        if (c === '}') {
            return;
        } else if (c === '"') {
            findString(reader);
        } else if (c === ':') {
            if (findValue(reader)) {
                return;
            }
        }
    }
}

function findArray(reader: StringReader): void {
    //console.log('findArray');
    if (findValue(reader)) {
        return;
    }

    let workingIndex = 0;
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findArray: char=${c}, row=${row}, col=${col}`);
        if (c === ']') {
            return;
        }
        workingIndex += 1;
        if (findValue(reader)) {
            return;
        }
    }
}

function findString(reader: StringReader): string {
    let workingString = '';
    let result;
    while ((result = reader.next()) !== null) {
        const [c, row, col] = result;
        //console.log(`findString: char=${c}`);
        if (c === '"') {
            return workingString;
        } else {
            workingString += c;
        }
    }
    throw new Error('String not closed');
}
