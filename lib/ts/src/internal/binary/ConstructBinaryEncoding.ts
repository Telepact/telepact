import { UApiSchema } from "../../UApiSchema";
import { BinaryEncoding } from "../../internal/binary/BinaryEncoding";
import { createChecksum } from "../../internal/binary/CreateChecksum";
import { UUnion } from "../../internal/types/UUnion";
import { UStruct } from "../../internal/types/UStruct";
import { UFn } from "../../internal/types/UFn";
import { UFieldDeclaration } from "../../internal/types/UFieldDeclaration";

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
            const unionTags: Record<string, UStruct> = value.tags;
            for (const [tagKey, tagValue] of Object.entries(unionTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }
        } else if (value instanceof UFn) {
            const fnCallTags: Record<string, UStruct> = value.call.tags;
            const fnResultTags: Record<string, UStruct> = value.result.tags;

            for (const [tagKey, tagValue] of Object.entries(fnCallTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
                for (const structFieldKey of Object.keys(structFields)) {
                    allKeys.add(structFieldKey);
                }
            }

            for (const [tagKey, tagValue] of Object.entries(fnResultTags)) {
                allKeys.add(tagKey);
                const structFields = tagValue.fields;
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

    const finalString = sortedAllKeys.join("\n");
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum);
}
