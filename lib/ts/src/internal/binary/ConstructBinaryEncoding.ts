import { UApiSchema } from 'uapi/UApiSchema';
import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { createChecksum } from 'uapi/internal/binary/CreateChecksum';
import { UUnion } from 'uapi/internal/types/UUnion';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UFn } from 'uapi/internal/types/UFn';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';

export function constructBinaryEncoding(uApiSchema: UApiSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();

    for (const [key, value] of Object.entries(uApiSchema.parsed)) {
        allKeys.add(key);

        if (value instanceof UStruct) {
            const structFields: Record<string, UFieldDeclaration> = value.fields;
            for (const structFieldKey of Object.keys(structFields)) {
                allKeys.add(structFieldKey);
            }
        } else if (value instanceof UUnion) {
            const unionCases: Record<string, UStruct> = value.cases;
            for (const [caseKey, caseValue] of Object.entries(unionCases)) {
                allKeys.add(caseKey);
                const structFields = caseValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
        } else if (value instanceof UFn) {
            const fnCallCases: Record<string, UStruct> = value.call.cases;
            const fnResultCases: Record<string, UStruct> = value.result.cases;

            for (const [caseKey, caseValue] of Object.entries(fnCallCases)) {
                allKeys.add(caseKey);
                const structFields = caseValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }

            for (const [caseKey, caseValue] of Object.entries(fnResultCases)) {
                allKeys.add(caseKey);
                const structFields = caseValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
        }
    }

    const sortedAllKeys = Array.from(allKeys).sort();
    const binaryEncoding = new Map<string, number>();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });

    const finalString = sortedAllKeys.join('\n');
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum);
}
