import { RandomGenerator } from '../../RandomGenerator';

export function generateRandomNumber(
    blueprintValue: any,
    useBlueprintValue: boolean,
    randomGenerator: RandomGenerator,
): any {
    if (useBlueprintValue) {
        return blueprintValue;
    } else {
        return randomGenerator.nextDouble();
    }
}
