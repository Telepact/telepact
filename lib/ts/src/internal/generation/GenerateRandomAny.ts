import { RandomGenerator } from 'uapi/RandomGenerator';

export function generateRandomAny(randomGenerator: RandomGenerator): any {
    const selectType = randomGenerator.nextIntWithCeiling(3);
    if (selectType === 0) {
        return randomGenerator.nextBoolean();
    } else if (selectType === 1) {
        return randomGenerator.nextInt();
    } else {
        return randomGenerator.nextString();
    }
}
