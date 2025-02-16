import { UApiSchema } from '../../UApiSchema';
import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { createChecksum } from '../../internal/binary/CreateChecksum';
import { UUnion } from '../../internal/types/UUnion';
import { UStruct } from '../../internal/types/UStruct';
import { UFn } from '../../internal/types/UFn';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UArray } from '../types/UArray';
import { UObject } from '../types/UObject';
import { UTypeDeclaration } from '../types/UTypeDeclaration';

export function constructBinaryEncoding(uApiSchema: UApiSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();

    const functions: [string, UFn][] = [];

    for (const [key, value] of Object.entries(uApiSchema.parsed)) {
        if (value instanceof UFn) {
            functions.push([key, value]);
        }
    }

    const traceType = (typeDeclaration: UTypeDeclaration) => {
        const thisAllKeys: string[] = [];

        if (typeDeclaration.type instanceof UArray) {
            const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
            thisAllKeys.push(...theseKeys2);
        } else if (typeDeclaration.type instanceof UObject) {
            const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
            thisAllKeys.push(...theseKeys2);
        } else if (typeDeclaration.type instanceof UStruct) {
            const structFields = typeDeclaration.type.fields;
            for (const [structFieldKey, structField] of Object.entries(structFields)) {
                thisAllKeys.push(structFieldKey);
                const moreKeys = traceType(structField.typeDeclaration);
                thisAllKeys.push(...moreKeys);
            }
        } else if (typeDeclaration.type instanceof UUnion) {
            const unionTags = typeDeclaration.type.tags;
            for (const [tagKey, tagValue] of Object.entries(unionTags)) {
                thisAllKeys.push(tagKey);
                const structFields = tagValue.fields;
                for (const [structFieldKey, structField] of Object.entries(structFields)) {
                    thisAllKeys.push(structFieldKey);
                    const moreKeys = traceType(structField.typeDeclaration);
                    thisAllKeys.push(...moreKeys);
                }
            }
        }

        return thisAllKeys;
    };

    for (const [key, value] of functions) {
        allKeys.add(key);
        const args = value.call.tags[key];
        Object.entries(args.fields).forEach(([fieldKey, field]) => {
            allKeys.add(fieldKey);
            const keys = traceType(field.typeDeclaration);
            keys.forEach((key) => allKeys.add(key));
        });

        const result = value.result.tags['Ok_'];
        allKeys.add('Ok_');
        Object.entries(result.fields).forEach(([fieldKey, field]) => {
            allKeys.add(fieldKey);
            const keys = traceType(field.typeDeclaration);
            keys.forEach((key) => allKeys.add(key));
        });
    }

    const sortedAllKeys = Array.from(allKeys).sort();

    console.log('Sorted all keys:');
    console.log(sortedAllKeys);

    const binaryEncoding = new Map<string, number>();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });

    const finalString = sortedAllKeys.join('\n');
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum);
}
