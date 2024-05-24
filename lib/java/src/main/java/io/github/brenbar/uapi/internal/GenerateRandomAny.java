package io.github.brenbar.uapi.internal;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomAny {
    static Object generateRandomAny(RandomGenerator randomGenerator) {
        final var selectType = randomGenerator.nextIntWithCeiling(3);
        if (selectType == 0) {
            return randomGenerator.nextBoolean();
        } else if (selectType == 1) {
            return randomGenerator.nextInt();
        } else {
            return randomGenerator.nextString();
        }
    }
}
