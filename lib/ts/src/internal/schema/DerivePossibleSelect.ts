import { UType } from "../types/UType";
import { UUnion } from "../types/UUnion";
import { UFn } from "../types/UFn";
import { UStruct } from "../types/UStruct";
import { UFieldDeclaration } from "../types/UFieldDeclaration";

export function derivePossibleSelect(fnName: string, result: UUnion): Record<string, any> {
    const nestedTypes: Record<string, UType> = {};
    const okFields: Record<string, UFieldDeclaration> = result.tags["Ok_"].fields;

    const okFieldNames = Object.keys(okFields);
    okFieldNames.sort();

    findNestedTypes(okFields, nestedTypes);

    const possibleSelect: Record<string, object> = {};

    possibleSelect["->"] = {
        Ok_: okFieldNames,
    };

    const sortedTypeKeys = Object.keys(nestedTypes).sort();
    for (const k of sortedTypeKeys) {
        console.log(`k: ${k}`);
        const v = nestedTypes[k];
        if (v instanceof UUnion) {
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
        } else if (v instanceof UStruct) {
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

function findNestedTypes(fields: Record<string, UFieldDeclaration>, nestedTypes: Record<string, UType>) {
    for (const field of Object.values(fields)) {
        const typ = field.typeDeclaration.type;
        if (typ instanceof UUnion) {
            nestedTypes[typ.name] = typ;
            for (const c of Object.values(typ.tags)) {
                findNestedTypes(c.fields, nestedTypes);
            }
        } else if (typ instanceof UStruct) {
            nestedTypes[typ.name] = typ;
            findNestedTypes(typ.fields, nestedTypes);
        }
    }
}
