package io.github.brenbar.japi;

import java.nio.ByteBuffer;
import java.util.Base64;

public class MockRandom {
    private int seed;

    public void setSeed(int seed) {
        this.seed = seed;
    }

    public int nextInt() {
        this.seed = (this.seed * 1_103_515_245 + 12_345) & 0x7fffffff;
        return seed;
    }

    public int nextInt(int ceiling) {
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
}
