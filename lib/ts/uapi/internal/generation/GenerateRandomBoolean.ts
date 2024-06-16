import { RandomGenerator } from 'uapi/RandomGenerator';

export function generateRandomBoolean(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: RandomGenerator,
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextBoolean();
    }
}
