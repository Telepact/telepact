import { RandomGenerator } from '../../RandomGenerator';

export function generateRandomString(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: RandomGenerator,
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextString();
    }
}
