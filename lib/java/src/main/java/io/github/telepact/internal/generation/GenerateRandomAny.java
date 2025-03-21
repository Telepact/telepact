package io.github.telepact.internal.generation;

public class GenerateRandomAny {
    public static Object generateRandomAny(GenerateContext ctx) {
        final var selectType = ctx.randomGenerator.nextIntWithCeiling(3);
        if (selectType == 0) {
            return ctx.randomGenerator.nextBoolean();
        } else if (selectType == 1) {
            return ctx.randomGenerator.nextInt();
        } else {
            return ctx.randomGenerator.nextString();
        }
    }
}
