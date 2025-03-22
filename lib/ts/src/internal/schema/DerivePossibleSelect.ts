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

import { TType } from '../types/TType';
import { TUnion } from '../types/TUnion';
import { TFn } from '../types/TFn';
import { TStruct } from '../types/TStruct';
import { TFieldDeclaration } from '../types/TFieldDeclaration';

export function derivePossibleSelect(fnName: string, result: TUnion): Record<string, any> {
    const nestedTypes: Record<string, TType> = {};
    const okFields: Record<string, TFieldDeclaration> = result.tags['Ok_'].fields;

    const okFieldNames = Object.keys(okFields);
    okFieldNames.sort();

    findNestedTypes(okFields, nestedTypes);

    const possibleSelect: Record<string, object> = {};

    possibleSelect['->'] = {
        Ok_: okFieldNames,
    };

    const sortedTypeKeys = Object.keys(nestedTypes).sort();
    for (const k of sortedTypeKeys) {
        console.log(`k: ${k}`);
        const v = nestedTypes[k];
        if (v instanceof TUnion) {
            const unionSelect: Record<string, object> = {};
            const sortedTagKeys = Object.keys(v.tags).sort();
            for (const c of sortedTagKeys) {
                const typ = v.tags[c];
                const selectedFieldNames: Array<string> = [];
                const sortedFieldNames = Object.keys(typ.fields).sort();
                for (const fieldName of sortedFieldNames) {
                    selectedFieldNames.push(fieldName);
                }

                unionSelect[c] = selectedFieldNames;
            }

            possibleSelect[k] = unionSelect;
        } else if (v instanceof TStruct) {
            const structSelect: Array<string> = [];
            const sortedFieldNames = Object.keys(v.fields).sort();
            for (const fieldName of sortedFieldNames) {
                structSelect.push(fieldName);
            }

            possibleSelect[k] = structSelect;
        }
    }

    return possibleSelect;
}

function findNestedTypes(fields: Record<string, TFieldDeclaration>, nestedTypes: Record<string, TType>) {
    for (const field of Object.values(fields)) {
        const typ = field.typeDeclaration.type;
        if (typ instanceof TUnion) {
            nestedTypes[typ.name] = typ;
            for (const c of Object.values(typ.tags)) {
                findNestedTypes(c.fields, nestedTypes);
            }
        } else if (typ instanceof TStruct) {
            nestedTypes[typ.name] = typ;
            findNestedTypes(typ.fields, nestedTypes);
        }
    }
}
