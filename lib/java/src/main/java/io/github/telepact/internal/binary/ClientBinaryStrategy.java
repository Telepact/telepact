//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.binary;

import java.time.Instant;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

class ClientBinaryStrategy {

    private static class Checksum {
        public final int value;
        public int expiration;

        public Checksum(int value, int expiration) {
            this.value = value;
            this.expiration = expiration;
        }
    }

    private Checksum primary = null;
    private Checksum secondary = null;
    private Instant lastUpdate = Instant.now();
    private final ReentrantLock lock = new ReentrantLock();
    private final BinaryEncodingCache binaryEncodingCache;

    public ClientBinaryStrategy(BinaryEncodingCache binaryEncodingCache) {
        this.binaryEncodingCache = binaryEncodingCache;
    }

    public void updateChecksum(Integer newChecksum) {
        try {
            lock.lock();

            if (this.primary == null) {
                this.primary = new Checksum(newChecksum, 0);
                return;
            }

            if (this.primary.value != newChecksum) {
                final var expiredChecksum = this.secondary;
                this.secondary = this.primary;
                this.primary = new Checksum(newChecksum, 0);
                this.secondary.expiration += 1;

                if (expiredChecksum != null) {
                    this.binaryEncodingCache.remove(expiredChecksum.value);
                }

                return;
            }

            lastUpdate = Instant.now();
        } finally {
            lock.unlock();
        }
    }

    public List<Integer> getCurrentChecksums() {
        try {
            lock.lock();

            if (primary == null) {
                return List.of();
            } else if (secondary == null) {
                return List.of(primary.value);
            } else {
                var minutesSinceLastUpdate = (Instant.now().getEpochSecond() - lastUpdate.getEpochSecond()) / 60;

                // Every 10 minute interval of non-use is a penalty point
                var penalty = ((int) (Math.floor(minutesSinceLastUpdate / 10))) + 1;

                secondary.expiration += 1 * penalty;

                if (secondary.expiration > 5) {
                    secondary = null;
                    return List.of(primary.value);
                } else {
                    return List.of(primary.value, secondary.value);
                }
            }
        } finally {
            lock.unlock();
        }
    }

}
