package uapi;

import java.nio.ByteBuffer;
import java.util.Base64;

public class RandomGenerator {
    int seed = 0;
    private int collectionLengthMin;
    private int collectionLengthMax;
    private int count = 0;

    public RandomGenerator(int collectionLengthMin, int collectionLengthMax) {
        this.setSeed(0);
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    public void setSeed(int seed) {
        this.seed = (seed & 0x7ffffffe) + 1;
    }

    private static String findStack() {
        var i = 0;
        for (var stack : Thread.currentThread().getStackTrace()) {
            i += 1;
            if (i == 1) {
                continue;
            }
            var stackStr = String.valueOf(stack);
            if (!stackStr.contains("_RandomGenerator")) {
                return stackStr;
            }
        }
        throw new RuntimeException();
    }

    public int nextInt() {
        var x = this.seed;
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        this.seed = (x & 0x7ffffffe) + 1;
        this.count += 1;
        var result = this.seed;
        // System.out.println("%d %d %s".formatted(count, result, findStack()));
        return result;
    }

    public int nextIntWithCeiling(int ceiling) {
        if (ceiling == 0) {
            return 0;
        }
        return (int) nextInt() % ceiling;
    }

    public boolean nextBoolean() {
        return nextIntWithCeiling(31) > 15;
    }

    public String nextString() {
        var bytes = ByteBuffer.allocate(Integer.BYTES);
        bytes.putInt(nextInt());
        return Base64.getEncoder().withoutPadding().encodeToString(bytes.array());
    }

    public double nextDouble() {
        return ((double) (nextInt() & 0x7fffffff) / ((double) 0x7fffffff));
    }

    public int nextCollectionLength() {
        return nextIntWithCeiling(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}
