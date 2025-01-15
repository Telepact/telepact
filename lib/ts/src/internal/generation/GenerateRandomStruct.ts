import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export function generateRandomStruct(referenceStruct: { [key: string]: UFieldDeclaration }, ctx: GenerateContext): any {
    const startingStruct = ctx.useBlueprintValue ? ctx.blueprintValue : {};

    const sortedReferenceStruct = Array.from(Object.entries(referenceStruct)).sort((e1, e2) => {
        const a = e1[0];
        const b = e2[0];
        for (let i = 0; i < Math.min(a.length, b.length); i++) {
            const charCodeA = a.charCodeAt(i);
            const charCodeB = b.charCodeAt(i);
            if (charCodeA !== charCodeB) {
                // If the characters are different, return the comparison result
                // where lowercase letters are considered greater than uppercase letters
                return charCodeA - charCodeB;
            }
        }
        // If one string is a prefix of the other, the shorter string comes first
        return a.length - b.length;
    });

    const obj: Record<string, any> = {};
    for (const [fieldName, fieldDeclaration] of sortedReferenceStruct) {
        const blueprintValue = startingStruct[fieldName];
        const useBlueprintValue = fieldName in startingStruct;
        const typeDeclaration = fieldDeclaration.typeDeclaration;

        let value: any;
        if (useBlueprintValue) {
            value = typeDeclaration.generateRandomValue(
                ctx.copy({ blueprintValue: blueprintValue, useBlueprintValue: useBlueprintValue }),
            );
        } else {
            if (!fieldDeclaration.optional) {
                value = typeDeclaration.generateRandomValue(
                    ctx.copy({ blueprintValue: null, useBlueprintValue: false }),
                );
            } else {
                if (!ctx.includeOptionalFields || (ctx.randomizeOptionalFields && ctx.randomGenerator.nextBoolean())) {
                    continue;
                }
                value = typeDeclaration.generateRandomValue(
                    ctx.copy({ blueprintValue: null, useBlueprintValue: false }),
                );
            }
        }

        obj[fieldName] = value;
    }

    return obj;
}
