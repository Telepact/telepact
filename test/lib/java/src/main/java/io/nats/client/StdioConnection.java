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

package io.nats.client;

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

class StdioConnection implements Connection {
    private static final String PROTO_PREFIX = "@@TPSTDIO@@";

    private final ObjectMapper mapper = new ObjectMapper();
    private final Object writeLock = new Object();
    private final ExecutorService callbackExecutor = Executors.newCachedThreadPool();

    private final AtomicLong sidCounter = new AtomicLong(0);
    private final AtomicLong ridCounter = new AtomicLong(0);

    private final Map<String, StdioDispatcher> sidDispatchers = new ConcurrentHashMap<>();
    private final Map<String, CompletableFuture<byte[]>> pendingRequests = new ConcurrentHashMap<>();

    private volatile boolean closed = false;
    private final Thread readerThread;

    StdioConnection(Options options) {
        // options.server is intentionally ignored; stdio transport has no endpoint.
        if (options != null && options.server != null) {
            // no-op
        }

        this.readerThread = new Thread(this::readLoop, "telepact-stdio-reader");
        this.readerThread.setDaemon(true);
        this.readerThread.start();
    }

    @Override
    public Message request(String subject, byte[] data, Duration timeout) throws InterruptedException {
        if (closed) {
            throw new InterruptedException("connection is closed");
        }

        var rid = "rid-" + ridCounter.incrementAndGet();
        var pending = new CompletableFuture<byte[]>();
        pendingRequests.put(rid, pending);

        send(Map.of(
                "op", "request",
                "rid", rid,
                "subject", subject,
                "timeout_ms", Math.max(timeout.toMillis(), 1),
                "data", Base64.getEncoder().encodeToString(data)));

        try {
            var payload = pending.get(Math.max(timeout.toMillis(), 1), TimeUnit.MILLISECONDS);
            return new Message(payload, null);
        } catch (TimeoutException e) {
            pendingRequests.remove(rid);
            throw new InterruptedException("request timed out");
        } catch (ExecutionException e) {
            var cause = e.getCause();
            if (cause instanceof InterruptedException) {
                throw (InterruptedException) cause;
            }
            throw new RuntimeException(cause);
        }
    }

    @Override
    public void publish(String subject, byte[] data) {
        if (closed) {
            throw new RuntimeException("connection is closed");
        }
        send(Map.of(
                "op", "publish",
                "subject", subject,
                "data", Base64.getEncoder().encodeToString(data)));
    }

    @Override
    public Dispatcher createDispatcher(MessageHandler messageHandler) {
        return new StdioDispatcher(this, messageHandler);
    }

    @Override
    public void close() {
        if (closed) {
            return;
        }
        closed = true;
        callbackExecutor.shutdownNow();
        failPendingRequests(new InterruptedException("connection closed"));
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
                failPendingRequests(e);
            }
        } finally {
            failPendingRequests(new InterruptedException("stdio input closed"));
        }
    }

    private void handleFrame(Map<String, Object> frame) {
        var op = (String) frame.get("op");
        if (op == null) {
            return;
        }

        switch (op) {
            case "message" -> {
                var sid = (String) frame.get("sid");
                if (sid == null) {
                    return;
                }
                var dispatcher = sidDispatchers.get(sid);
                if (dispatcher == null) {
                    return;
                }

                var dataB64 = (String) frame.get("data");
                if (dataB64 == null) {
                    return;
                }
                byte[] data = Base64.getDecoder().decode(dataB64);
                String reply = (String) frame.get("reply");

                callbackExecutor.execute(() -> dispatcher.onMessage(new Message(data, reply)));
            }
            case "request_result" -> {
                var rid = (String) frame.get("rid");
                if (rid == null) {
                    return;
                }
                var pending = pendingRequests.remove(rid);
                if (pending == null) {
                    return;
                }

                var ok = Boolean.TRUE.equals(frame.get("ok"));
                if (ok) {
                    var dataB64 = (String) frame.get("data");
                    if (dataB64 == null) {
                        pending.completeExceptionally(new RuntimeException("missing response payload"));
                        return;
                    }
                    pending.complete(Base64.getDecoder().decode(dataB64));
                } else {
                    var error = (String) frame.getOrDefault("error", "request failed");
                    pending.completeExceptionally(new RuntimeException(error));
                }
            }
            default -> {
                // no-op
            }
        }
    }

    private void send(Map<String, Object> frame) {
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

    private void failPendingRequests(Exception error) {
        for (var entry : pendingRequests.entrySet()) {
            if (pendingRequests.remove(entry.getKey()) != null) {
                entry.getValue().completeExceptionally(error);
            }
        }
    }

    String registerSubscription(StdioDispatcher dispatcher, String subject) {
        var sid = "sid-" + sidCounter.incrementAndGet();
        sidDispatchers.put(sid, dispatcher);
        send(Map.of(
                "op", "subscribe",
                "sid", sid,
                "subject", subject));
        return sid;
    }

    void unregisterSubscription(String sid) {
        sidDispatchers.remove(sid);
        send(Map.of(
                "op", "unsubscribe",
                "sid", sid));
    }

    private static final class StdioDispatcher implements Dispatcher {
        private final StdioConnection connection;
        private final MessageHandler handler;
        private final Set<String> sids = ConcurrentHashMap.newKeySet();

        private StdioDispatcher(StdioConnection connection, MessageHandler handler) {
            this.connection = connection;
            this.handler = handler;
        }

        @Override
        public void subscribe(String subject) {
            var sid = connection.registerSubscription(this, subject);
            sids.add(sid);
        }

        @Override
        public CompletableFuture<Void> drain(Duration timeout) {
            if (timeout != null && timeout.isNegative()) {
                // no-op
            }
            for (var sid : sids) {
                connection.unregisterSubscription(sid);
            }
            sids.clear();
            return CompletableFuture.completedFuture(null);
        }

        void onMessage(Message message) {
            handler.onMessage(message);
        }
    }
}
