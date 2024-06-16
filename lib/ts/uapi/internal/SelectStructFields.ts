import { UArray } from 'uapi/internal/types/UArray';
import { UFn } from 'uapi/internal/types/UFn';
import { UObject } from 'uapi/internal/types/UObject';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UUnion } from 'uapi/internal/types/UUnion';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';

export function selectStructFields(
    typeDeclaration: UTypeDeclaration,
    value: any,
    selectedStructFields: { [key: string]: any },
): any {
    const typeDeclarationType = typeDeclaration.type;
    const typeDeclarationTypeParams = typeDeclaration.typeParameters;

    if (typeDeclarationType instanceof UStruct) {
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
    } else if (typeDeclarationType instanceof UFn) {
        const valueAsMap = value as { [key: string]: any };
        const [unionCase, unionData] = Object.entries(valueAsMap)[0];
        const fnName = typeDeclarationType.name;
        const fnCall = typeDeclarationType.call;
        const fnCallCases = fnCall.cases;

        const argStructReference = fnCallCases[unionCase];
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

        return { [unionCase]: finalMap };
    } else if (typeDeclarationType instanceof UUnion) {
        const valueAsMap = value as { [key: string]: any };
        const [unionCase, unionData] = Object.entries(valueAsMap)[0];

        const unionCases = typeDeclarationType.cases;
        const unionStructReference = unionCases[unionCase];
        const unionStructRefFields = unionStructReference.fields;
        const defaultCasesToFields: { [key: string]: string[] } = {};

        for (const [caseName, unionStruct] of Object.entries(unionCases)) {
            const fieldNames = Object.keys(unionStruct.fields);
            defaultCasesToFields[caseName] = fieldNames;
        }

        const unionSelectedFields = selectedStructFields[typeDeclarationType.name] as
            | { [key: string]: any }
            | undefined;
        const thisUnionCaseSelectedFieldsDefault = defaultCasesToFields[unionCase];
        const selectedFields = unionSelectedFields?.[unionCase] || thisUnionCaseSelectedFieldsDefault;

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

        return { [unionCase]: finalMap };
    } else if (typeDeclarationType instanceof UObject) {
        const nestedTypeDeclaration = typeDeclarationTypeParams[0];
        const valueAsMap = value as { [key: string]: any };

        const finalMap: { [key: string]: any } = {};
        for (const [key, value] of Object.entries(valueAsMap)) {
            const valueWithSelectedFields = selectStructFields(nestedTypeDeclaration, value, selectedStructFields);

            finalMap[key] = valueWithSelectedFields;
        }

        return finalMap;
    } else if (typeDeclarationType instanceof UArray) {
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
