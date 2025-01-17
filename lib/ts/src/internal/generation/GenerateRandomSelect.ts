import { GenerateContext } from './GenerateContext';

export function generateRandomSelect(possibleSelects: Record<string, any>, ctx: GenerateContext): object {
    const possibleSelect = possibleSelects[ctx.fnScope];
    return subSelect(possibleSelect, ctx);
}

function subSelect(possibleSelectSection: any, ctx: GenerateContext): any {
    if (Array.isArray(possibleSelectSection)) {
        const selectedFieldNames = [];

        for (const fieldName of possibleSelectSection) {
            if (ctx.randomGenerator.nextBoolean()) {
                selectedFieldNames.push(fieldName);
            }
        }

        return selectedFieldNames;
    } else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        const selectedSection: Record<string, any> = {};

        for (const [key, value] of Object.entries(possibleSelectSection)) {
            if (ctx.randomGenerator.nextBoolean()) {
                const result = subSelect(value, ctx);
                if (typeof result === 'object' && !Array.isArray(result) && Object.keys(result).length === 0) {
                    continue;
                }
                selectedSection[key] = result;
            }
        }

        return selectedSection;
    } else {
        throw new Error('Invalid possibleSelectSection');
    }
}
