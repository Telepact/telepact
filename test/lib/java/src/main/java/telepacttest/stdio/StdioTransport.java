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

package telepacttest.stdio;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Base64;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicLong;

import com.fasterxml.jackson.databind.ObjectMapper;

public class StdioTransport implements Transport {
    private static final String PROTO_PREFIX = "@@TPSTDIO@@";

    private final ObjectMapper mapper = new ObjectMapper();
    private final Object writeLock = new Object();
    private final ExecutorService callbackExecutor = Executors.newCachedThreadPool();

    private final AtomicLong lidCounter = new AtomicLong(0);
    private final AtomicLong cidCounter = new AtomicLong(0);

    private final Map<String, StdioListener> lidListeners = new ConcurrentHashMap<>();
    private final Map<String, CompletableFuture<byte[]>> pendingCalls = new ConcurrentHashMap<>();

    private volatile boolean closed = false;
    private final Thread readerThread;

    public StdioTransport(TransportConfig config) {
        // The endpoint is intentionally unused for stdio transport.
        if (config != null && config.endpoint != null) {
            // no-op
        }

        this.readerThread = new Thread(this::readLoop, "telepact-stdio-reader");
        this.readerThread.setDaemon(true);
        this.readerThread.start();
    }

    @Override
    public CallResult call(String channel, byte[] payload, Duration timeout) throws InterruptedException {
        if (closed) {
            throw new InterruptedException("transport is closed");
        }

        var cid = "cid-" + cidCounter.incrementAndGet();
        var pending = new CompletableFuture<byte[]>();
        pendingCalls.put(cid, pending);

        sendFrame(Map.of(
                "op", "call",
                "cid", cid,
                "channel", channel,
                "timeout_ms", Math.max(timeout.toMillis(), 1),
                "payload", Base64.getEncoder().encodeToString(payload)));

        try {
            var responsePayload = pending.get(Math.max(timeout.toMillis(), 1), TimeUnit.MILLISECONDS);
            return new CallResult(responsePayload);
        } catch (TimeoutException e) {
            pendingCalls.remove(cid);
            throw new InterruptedException("call timed out");
        } catch (ExecutionException e) {
            var cause = e.getCause();
            if (cause instanceof InterruptedException) {
                throw (InterruptedException) cause;
            }
            throw new RuntimeException(cause);
        }
    }

    @Override
    public void send(String channel, byte[] payload) {
        if (closed) {
            throw new RuntimeException("transport is closed");
        }
        sendFrame(Map.of(
                "op", "send",
                "channel", channel,
                "payload", Base64.getEncoder().encodeToString(payload)));
    }

    @Override
    public TransportListener openListener(TransportHandler handler) {
        return new StdioListener(this, handler);
    }

    @Override
    public void close() {
        if (closed) {
            return;
        }
        closed = true;
        callbackExecutor.shutdownNow();
        failPendingCalls(new InterruptedException("transport closed"));
    }

    private void readLoop() {
        try (var reader = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.startsWith(PROTO_PREFIX)) {
                    continue;
                }
                @SuppressWarnings("unchecked")
                var frame = mapper.readValue(line.substring(PROTO_PREFIX.length()), Map.class);
                handleFrame(frame);
            }
        } catch (Exception e) {
            if (!closed) {
                failPendingCalls(e);
            }
        } finally {
            failPendingCalls(new InterruptedException("stdio input closed"));
        }
    }

    private void handleFrame(Map<String, Object> frame) {
        var op = (String) frame.get("op");
        if (op == null) {
            return;
        }

        switch (op) {
            case "event" -> {
                var lid = (String) frame.get("lid");
                if (lid == null) {
                    return;
                }
                var listener = lidListeners.get(lid);
                if (listener == null) {
                    return;
                }

                var payloadB64 = (String) frame.get("payload");
                if (payloadB64 == null) {
                    return;
                }
                byte[] payload = Base64.getDecoder().decode(payloadB64);

                var replyChannel = (String) frame.get("reply_channel");
                callbackExecutor.execute(() -> listener.onMessage(new TransportMessage(this, payload, replyChannel)));
            }
            case "call_result" -> {
                var cid = (String) frame.get("cid");
                if (cid == null) {
                    return;
                }
                var pending = pendingCalls.remove(cid);
                if (pending == null) {
                    return;
                }

                var ok = Boolean.TRUE.equals(frame.get("ok"));
                if (ok) {
                    var payloadB64 = (String) frame.get("payload");
                    if (payloadB64 == null) {
                        pending.completeExceptionally(new RuntimeException("missing call response payload"));
                        return;
                    }
                    pending.complete(Base64.getDecoder().decode(payloadB64));
                } else {
                    var error = (String) frame.getOrDefault("error", "call failed");
                    pending.completeExceptionally(new RuntimeException(error));
                }
            }
            default -> {
                // no-op
            }
        }
    }

    private void sendFrame(Map<String, Object> frame) {
        try {
            var payload = mapper.writeValueAsString(frame);
            synchronized (writeLock) {
                System.out.println(PROTO_PREFIX + payload);
                System.out.flush();
            }
        } catch (Exception e) {
            throw new RuntimeException("failed to send stdio frame", e);
        }
    }

    private void failPendingCalls(Exception error) {
        for (var entry : pendingCalls.entrySet()) {
            if (pendingCalls.remove(entry.getKey()) != null) {
                entry.getValue().completeExceptionally(error);
            }
        }
    }

    String registerChannel(StdioListener listener, String channel) {
        var lid = "lid-" + lidCounter.incrementAndGet();
        lidListeners.put(lid, listener);
        sendFrame(Map.of(
                "op", "listen",
                "lid", lid,
                "channel", channel));
        return lid;
    }

    void unregisterChannel(String lid) {
        lidListeners.remove(lid);
        sendFrame(Map.of(
                "op", "unlisten",
                "lid", lid));
    }

    private static final class StdioListener implements TransportListener {
        private final StdioTransport transport;
        private final TransportHandler handler;
        private final Set<String> lids = ConcurrentHashMap.newKeySet();

        private StdioListener(StdioTransport transport, TransportHandler handler) {
            this.transport = transport;
            this.handler = handler;
        }

        @Override
        public void listen(String channel) {
            var lid = transport.registerChannel(this, channel);
            lids.add(lid);
        }

        @Override
        public CompletableFuture<Void> close(Duration timeout) {
            if (timeout != null && timeout.isNegative()) {
                // no-op
            }
            for (var lid : lids) {
                transport.unregisterChannel(lid);
            }
            lids.clear();
            return CompletableFuture.completedFuture(null);
        }

        void onMessage(TransportMessage message) {
            handler.onMessage(message);
        }
    }
}
