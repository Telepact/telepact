package io.github.brenbar.japi;

import java.time.Instant;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class _DefaultBinaryChecksumStrategy implements BinaryChecksumStrategy {

    private static class Checksum {
        public final int value;
        public AtomicInteger expiration;

        public Checksum(int value, AtomicInteger expiration) {
            this.value = value;
            this.expiration = expiration;
        }
    }

    private Checksum primary = null;
    private Checksum secondary = null;
    private Instant lastUpdate = Instant.now();

    @Override
    public void update(Integer newChecksum) {
        if (this.primary == null) {
            this.primary = new Checksum(newChecksum, new AtomicInteger());
            return;
        }

        if (this.primary.value != newChecksum) {
            this.secondary = this.primary;
            this.primary = new Checksum(newChecksum, new AtomicInteger());
            this.secondary.expiration.incrementAndGet();
            return;
        }

        lastUpdate = Instant.now();
    }

    @Override
    public List<Integer> get() {
        if (primary == null) {
            return List.of();
        } else if (secondary == null) {
            return List.of(primary.value);
        } else {
            var minutesSinceLastUpdate = (Instant.now().getEpochSecond() - lastUpdate.getEpochSecond()) / 60;

            // Every 10 minute interval of non-use is a penalty point
            var penalty = ((int) (Math.floor(minutesSinceLastUpdate / 10))) + 1;

            secondary.expiration.addAndGet(1 * penalty);
            System.out.println("%d %d".formatted(secondary.value, secondary.expiration.get()));
            if (secondary.expiration.get() > 5) {
                secondary = null;
                return List.of(primary.value);
            } else {
                return List.of(primary.value, secondary.value);
            }
        }
    }

}
