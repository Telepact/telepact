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

package io.github.telepact.internal;

import java.util.ArrayDeque;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Supplier;

import io.github.telepact.SerializerMeasurement;

public final class SerializerMeasurementSupport {

    private SerializerMeasurementSupport() {
    }

    private static final ThreadLocal<ArrayDeque<MeasurementContext>> CONTEXT_STACK = ThreadLocal
            .withInitial(ArrayDeque::new);

    public static <T> T runMeasuredSerializerOperation(
            String operation,
            Consumer<SerializerMeasurement> observer,
            boolean binaryRequested,
            String transportEncoding,
            String protocolEncoding,
            boolean packed,
            boolean fellBackToJson,
            Supplier<T> supplier) {
        var context = new MeasurementContext(new MutableMeasurement(
                operation,
                binaryRequested,
                transportEncoding,
                protocolEncoding,
                packed,
                fellBackToJson), observer);
        var stack = CONTEXT_STACK.get();
        stack.push(context);
        long startedAtNs = System.nanoTime();
        try {
            return supplier.get();
        } finally {
            context.measurement.totalDurationNs = System.nanoTime() - startedAtNs;
            stack.pop();
            context.observer.accept(snapshot(context.measurement));
        }
    }

    public static <T> T measureSerializerStage(String stageName, Supplier<T> supplier) {
        var context = currentContext();
        if (context == null) {
            return supplier.get();
        }
        long startedAtNs = System.nanoTime();
        try {
            return supplier.get();
        } finally {
            recordStage(context.measurement, stageName, System.nanoTime() - startedAtNs);
        }
    }

    public static void measureSerializerStage(String stageName, Runnable runnable) {
        measureSerializerStage(stageName, () -> {
            runnable.run();
            return null;
        });
    }

    public static <T> T measureSerializerStageThrowable(String stageName, ThrowingSupplier<T> supplier) throws Throwable {
        var context = currentContext();
        if (context == null) {
            return supplier.get();
        }
        long startedAtNs = System.nanoTime();
        try {
            return supplier.get();
        } finally {
            recordStage(context.measurement, stageName, System.nanoTime() - startedAtNs);
        }
    }

    public static void measureSerializerStageThrowable(String stageName, ThrowingRunnable runnable) throws Throwable {
        measureSerializerStageThrowable(stageName, () -> {
            runnable.run();
            return null;
        });
    }

    public static void annotateSerializerMeasurement(
            Boolean binaryRequested,
            String transportEncoding,
            String protocolEncoding,
            Boolean packed,
            Boolean fellBackToJson) {
        var context = currentContext();
        if (context == null) {
            return;
        }
        if (binaryRequested != null) {
            context.measurement.binaryRequested = binaryRequested;
        }
        if (transportEncoding != null) {
            context.measurement.transportEncoding = transportEncoding;
        }
        if (protocolEncoding != null) {
            context.measurement.protocolEncoding = protocolEncoding;
        }
        if (packed != null) {
            context.measurement.packed = packed;
        }
        if (fellBackToJson != null) {
            context.measurement.fellBackToJson = fellBackToJson;
        }
    }

    private static MeasurementContext currentContext() {
        var stack = CONTEXT_STACK.get();
        return stack.isEmpty() ? null : stack.peek();
    }

    private static void recordStage(MutableMeasurement measurement, String stageName, long durationNs) {
        var stage = measurement.stages.computeIfAbsent(stageName, ignored -> new MutableStage());
        stage.totalDurationNs += durationNs;
        stage.count += 1;
    }

    private static SerializerMeasurement snapshot(MutableMeasurement measurement) {
        Map<String, SerializerMeasurement.Stage> stages = new LinkedHashMap<>();
        for (var entry : measurement.stages.entrySet()) {
            stages.put(entry.getKey(), new SerializerMeasurement.Stage(
                    entry.getValue().totalDurationNs,
                    entry.getValue().count));
        }
        return new SerializerMeasurement(
                measurement.operation,
                measurement.totalDurationNs,
                measurement.binaryRequested,
                measurement.transportEncoding,
                measurement.protocolEncoding,
                measurement.packed,
                measurement.fellBackToJson,
                Map.copyOf(stages));
    }

    private record MeasurementContext(MutableMeasurement measurement, Consumer<SerializerMeasurement> observer) {
        private MeasurementContext(MutableMeasurement measurement, Consumer<SerializerMeasurement> observer) {
            this.measurement = measurement;
            this.observer = observer != null ? observer : ignored -> {
            };
        }
    }

    private static final class MutableMeasurement {
        private final String operation;
        private long totalDurationNs;
        private boolean binaryRequested;
        private String transportEncoding;
        private String protocolEncoding;
        private boolean packed;
        private boolean fellBackToJson;
        private final Map<String, MutableStage> stages = new LinkedHashMap<>();

        private MutableMeasurement(
                String operation,
                boolean binaryRequested,
                String transportEncoding,
                String protocolEncoding,
                boolean packed,
                boolean fellBackToJson) {
            this.operation = operation;
            this.binaryRequested = binaryRequested;
            this.transportEncoding = transportEncoding;
            this.protocolEncoding = protocolEncoding;
            this.packed = packed;
            this.fellBackToJson = fellBackToJson;
        }
    }

    private static final class MutableStage {
        private long totalDurationNs;
        private long count;
    }

    @FunctionalInterface
    public interface ThrowingSupplier<T> {
        T get() throws Throwable;
    }

    @FunctionalInterface
    public interface ThrowingRunnable {
        void run() throws Throwable;
    }
}
