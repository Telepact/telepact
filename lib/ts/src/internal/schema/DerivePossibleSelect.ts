//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TType } from '../types/TType.js';
import { TUnion } from '../types/TUnion.js';
import { TStruct } from '../types/TStruct.js';
import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { TArray } from '../types/TArray.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { TObject } from '../types/TObject.js';

export function derivePossibleSelect(fnName: string, result: TUnion): Record<string, any> {
    const nestedTypes: Record<string, TType> = {};
    const okFields: Record<string, TFieldDeclaration> = result.tags['Ok_'].fields;

    const okFieldNames = Object.keys(okFields);
    okFieldNames.sort();

    for (const fieldDecl of Object.values(okFields)) {
        findNestedTypes(fieldDecl.typeDeclaration, nestedTypes);
    }

    const possibleSelect: Record<string, object> = {};

    possibleSelect['->'] = {
        Ok_: okFieldNames,
    };

    const sortedTypeKeys = Object.keys(nestedTypes).sort();
    for (const k of sortedTypeKeys) {
        if (k.startsWith('fn.')) {
            continue;
        }

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

                if (selectedFieldNames.length > 0) {
                    unionSelect[c] = selectedFieldNames;
                }
            }

            possibleSelect[k] = unionSelect;
        } else if (v instanceof TStruct) {
            const structSelect: Array<string> = [];
            const sortedFieldNames = Object.keys(v.fields).sort();
            for (const fieldName of sortedFieldNames) {
                structSelect.push(fieldName);
            }

            if (structSelect.length > 0) {
                possibleSelect[k] = structSelect;
            }
        }
    }

    return possibleSelect;
}

function findNestedTypes(typeDeclaration: TTypeDeclaration, nestedTypes: Record<string, TType>) {
    const typ = typeDeclaration.type;
    if (typ instanceof TUnion) {
        if (nestedTypes[typ.name] !== undefined) {
            return;
        }
        nestedTypes[typ.name] = typ;
        for (const tag of Object.values(typ.tags)) {
            for (const fieldDecl of Object.values(tag.fields)) {
                findNestedTypes(fieldDecl.typeDeclaration, nestedTypes);
            }
        }
    } else if (typ instanceof TStruct) {
        if (nestedTypes[typ.name] !== undefined) {
            return;
        }
        nestedTypes[typ.name] = typ;
        for (const fieldDecl of Object.values(typ.fields)) {
            findNestedTypes(fieldDecl.typeDeclaration, nestedTypes);
        }
    } else if (typ instanceof TArray || typ instanceof TObject) {
        findNestedTypes(typeDeclaration.typeParameters[0], nestedTypes);
    }
}
