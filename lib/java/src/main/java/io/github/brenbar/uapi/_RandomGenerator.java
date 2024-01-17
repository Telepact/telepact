package io.github.brenbar.uapi;

import java.nio.ByteBuffer;
import java.util.Base64;

class _RandomGenerator {
    private int seed = 0;
    private int collectionLengthMin;
    private int collectionLengthMax;

    public _RandomGenerator(int collectionLengthMin, int collectionLengthMax) {
        this.collectionLengthMin = collectionLengthMin;
        this.collectionLengthMax = collectionLengthMax;
    }

    public void setSeed(int seed) {
        this.seed = seed;
    }

    public int nextInt() {
        this.seed = (this.seed * 1_103_515_245 + 12_345) & 0x7fffffff;
        return seed;
    }

    public int nextInt(int ceiling) {
        if (ceiling == 0) {
            return 0;
        }
        return (int) nextInt() % ceiling;
    }

    public boolean nextBoolean() {
        return nextInt(31) > 15;
    }

    public String nextString() {
        var bytes = ByteBuffer.allocate(Integer.BYTES);
        bytes.putInt(nextInt());
        return Base64.getEncoder().withoutPadding().encodeToString(bytes.array());
    }

    public double nextDouble() {
        var x = (double) (nextInt(Integer.MAX_VALUE / 2) + (Integer.MAX_VALUE / 4));
        var y = Integer.MAX_VALUE;
        return x / (x + y);
    }

    public int nextCollectionLength() {
        return nextInt(this.collectionLengthMax - this.collectionLengthMin) + this.collectionLengthMin;
    }
}
