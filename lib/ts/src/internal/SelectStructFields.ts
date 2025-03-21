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

import { VArray } from './types/VArray';
import { VFn } from './types/VFn';
import { VObject } from './types/VObject';
import { VStruct } from './types/VStruct';
import { VUnion } from './types/VUnion';
import { VTypeDeclaration } from './types/VTypeDeclaration';

export function selectStructFields(
    typeDeclaration: VTypeDeclaration,
    value: any,
    selectedStructFields: { [key: string]: any },
): any {
    const typeDeclarationType = typeDeclaration.type;
    const typeDeclarationTypeParams = typeDeclaration.typeParameters;

    if (typeDeclarationType instanceof VStruct) {
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
    } else if (typeDeclarationType instanceof VFn) {
        const valueAsMap = value as { [key: string]: any };
        const [unionTag, unionData] = Object.entries(valueAsMap)[0];
        const fnName = typeDeclarationType.name;
        const fnCall = typeDeclarationType.call;
        const fnCallTags = fnCall.tags;

        const argStructReference = fnCallTags[unionTag];
        const selectedFields = selectedStructFields[fnName] as string[] | undefined;
        const finalMap: { [key: string]: any } = {};

        for (const [fieldName, fieldValue] of Object.entries(unionData)) {
            if (selectedFields === undefined || selectedFields.includes(fieldName)) {
                const field = argStructReference.fields[fieldName];
                const valueWithSelectedFields = selectStructFields(
                    field.typeDeclaration,
                    fieldValue,
                    selectedStructFields,
                );

                finalMap[fieldName] = valueWithSelectedFields;
            }
        }

        return { [unionTag]: finalMap };
    } else if (typeDeclarationType instanceof VUnion) {
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
    } else if (typeDeclarationType instanceof VObject) {
        const nestedTypeDeclaration = typeDeclarationTypeParams[0];
        const valueAsMap = value as { [key: string]: any };

        const finalMap: { [key: string]: any } = {};
        for (const [key, value] of Object.entries(valueAsMap)) {
            const valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, value, selectedStructFields);

            finalMap[key] = valueWithSelectedFields;
        }

        return finalMap;
    } else if (typeDeclarationType instanceof VArray) {
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
