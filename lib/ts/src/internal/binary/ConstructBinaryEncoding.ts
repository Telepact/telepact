import { MsgPactSchema } from '../../MsgPactSchema';
import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { createChecksum } from '../../internal/binary/CreateChecksum';
import { VUnion } from '../types/VUnion';
import { VStruct } from '../types/VStruct';
import { VFn } from '../types/VFn';
import { VArray } from '../types/VArray';
import { VObject } from '../types/VObject';
import { VTypeDeclaration } from '../types/VTypeDeclaration';

function traceType(typeDeclaration: VTypeDeclaration): string[] {
    const thisAllKeys: string[] = [];

    if (typeDeclaration.type instanceof VArray) {
        const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
        thisAllKeys.push(...theseKeys2);
    } else if (typeDeclaration.type instanceof VObject) {
        const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
        thisAllKeys.push(...theseKeys2);
    } else if (typeDeclaration.type instanceof VStruct) {
        const structFields = typeDeclaration.type.fields;
        for (const [structFieldKey, structField] of Object.entries(structFields)) {
            thisAllKeys.push(structFieldKey);
            const moreKeys = traceType(structField.typeDeclaration);
            thisAllKeys.push(...moreKeys);
        }
    } else if (typeDeclaration.type instanceof VUnion) {
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
}

export function constructBinaryEncoding(msgPactSchema: MsgPactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();

    const functions: [string, VFn][] = [];

    for (const [key, value] of Object.entries(msgPactSchema.parsed)) {
        if (value instanceof VFn) {
            functions.push([key, value]);
        }
    }

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
