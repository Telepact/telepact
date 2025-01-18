package uapi.internal.generation;

public class GenerateRandomInteger {
    public static Object generateRandomInteger(Object blueprintValue, boolean useBlueprintValue, GenerateContext ctx) {
        if (useBlueprintValue) {
            return blueprintValue;
        } else {
            return ctx.randomGenerator.nextInt();
        }
    }
}
