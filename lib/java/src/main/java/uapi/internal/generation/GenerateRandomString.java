package uapi.internal.generation;

import uapi.RandomGenerator;

public class GenerateRandomString {
    public static Object generateRandomString(Object blueprintValue, boolean useBlueprintValue,
            RandomGenerator randomGenerator) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return randomGenerator.nextString();
        }
    }
}
