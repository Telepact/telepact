import { RandomGenerator } from 'uapi/RandomGenerator';

export function generateRandomInteger(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: RandomGenerator,
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextInt();
    }
}
