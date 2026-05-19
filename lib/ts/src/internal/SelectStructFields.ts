//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TArray } from './types/TArray.js';
import { TObject } from './types/TObject.js';
import { TStruct } from './types/TStruct.js';
import { TUnion } from './types/TUnion.js';
import { TTypeDeclaration } from './types/TTypeDeclaration.js';

export function selectStructFields(
    typeDeclaration: TTypeDeclaration,
    value: any,
    selectedStructFields: { [key: string]: any },
): any {
    const typeDeclarationType = typeDeclaration.type;
    const typeDeclarationTypeParams = typeDeclaration.typeParameters;

    if (typeDeclarationType instanceof TStruct) {
        const fields = typeDeclarationType.fields;
        const structName = typeDeclarationType.name;
        const selectedFields = selectedStructFields[structName] as string[] | undefined;
        const valueAsMap = value as { [key: string]: any };
        const finalMap: { [key: string]: any } = {};

        for (const [fieldName, fieldValue] of Object.entries(valueAsMap)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = fields[fieldName];
                const fieldTypeDeclaration = field.typeDeclaration;
                const valueWithSelectedFields = selectStructFields(
                    fieldTypeDeclaration,
                    fieldValue,
                    selectedStructFields,
                );

                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return finalMap;
    } else if (typeDeclarationType instanceof TUnion) {
        if (typeDeclarationType.name.startsWith('fn.')) {
            return value;
        }

        const valueAsMap = value as { [key: string]: any };
        const [unionTag, unionData] = Object.entries(valueAsMap)[0];

        const unionTags = typeDeclarationType.tags;
        const unionStructReference = unionTags[unionTag];
        const unionStructRefFields = unionStructReference.fields;
        const defaultTagsToFields: { [key: string]: string[] } = {};

        for (const [tagName, unionStruct] of Object.entries(unionTags)) {
            const fieldNames = Object.keys(unionStruct.fields);
            defaultTagsToFields[tagName] = fieldNames;
        }

        const unionSelectedFields = selectedStructFields[typeDeclarationType.name] as
            | { [key: string]: any }
            | undefined;
        const thisUnionTagSelectedFieldsDefault = defaultTagsToFields[unionTag];
        const selectedFields = unionSelectedFields?.[unionTag] || thisUnionTagSelectedFieldsDefault;

        const finalMap: { [key: string]: any } = {};
        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = unionStructRefFields[fieldName];
                const valueWithSelectedFields = selectStructFields(
                    field.typeDeclaration,
                    fieldValue,
                    selectedStructFields,
                );

                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return { [unionTag]: finalMap };
    } else if (typeDeclarationType instanceof TObject) {
        const nestedTypeDeclaration = typeDeclarationTypeParams[0];
        const valueAsMap = value as { [key: string]: any };

        const finalMap: { [key: string]: any } = {};
        for (const [key, value] of Object.entries(valueAsMap)) {
            const valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, value, selectedStructFields);

            finalMap[key] = valueWithSelectedFields;
        }

        return finalMap;
    } else if (typeDeclarationType instanceof TArray) {
        const nestedType = typeDeclarationTypeParams[0];
        const valueAsList = value as any[];

        const finalList: any[] = [];
        for (const entry of valueAsList) {
            const valueWithSelectedFields = selectStructFields(nestedType, entry, selectedStructFields);
            finalList.push(valueWithSelectedFields);
        }

        return finalList;
    } else {
        return value;
    }
}
