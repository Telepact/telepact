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

export type SerializerMeasurementOperation = 'serialize' | 'deserialize';
export type SerializerMeasurementTransportEncoding = 'json' | 'msgpack';
export type SerializerMeasurementProtocolEncoding = 'base64' | 'binary';

export type SerializerMeasurementStageStats = {
    totalDurationNs: number;
    count: number;
};

export type SerializerMeasurement = {
    operation: SerializerMeasurementOperation;
    totalDurationNs: number;
    binaryRequested: boolean;
    transportEncoding: SerializerMeasurementTransportEncoding;
    protocolEncoding: SerializerMeasurementProtocolEncoding;
    packed: boolean;
    fellBackToJson: boolean;
    stages: Record<string, SerializerMeasurementStageStats>;
};

export type SerializerMeasurementObserver = (measurement: SerializerMeasurement) => void;

type MutableSerializerMeasurement = SerializerMeasurement;

type SerializerMeasurementContext = {
    measurement: MutableSerializerMeasurement;
    observer?: SerializerMeasurementObserver;
};

const serializerMeasurementStack: SerializerMeasurementContext[] = [];

function nowNs(): number {
    if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
        return Math.round(performance.now() * 1_000_000);
    }
    return Date.now() * 1_000_000;
}

function currentSerializerMeasurementContext(): SerializerMeasurementContext | undefined {
    return serializerMeasurementStack[serializerMeasurementStack.length - 1];
}

function cloneSerializerMeasurement(measurement: MutableSerializerMeasurement): SerializerMeasurement {
    const stages = Object.fromEntries(
        Object.entries(measurement.stages).map(([stageName, stats]) => [
            stageName,
            { totalDurationNs: stats.totalDurationNs, count: stats.count },
        ]),
    );
    return {
        ...measurement,
        stages,
    };
}

function recordSerializerMeasurementStage(stageName: string, durationNs: number): void {
    const context = currentSerializerMeasurementContext();
    if (!context) {
        return;
    }
    const existing = context.measurement.stages[stageName];
    if (existing) {
        existing.totalDurationNs += durationNs;
        existing.count += 1;
    } else {
        context.measurement.stages[stageName] = {
            totalDurationNs: durationNs,
            count: 1,
        };
    }
}

export function annotateSerializerMeasurement(values: Partial<Omit<SerializerMeasurement, 'operation' | 'totalDurationNs' | 'stages'>>): void {
    const context = currentSerializerMeasurementContext();
    if (!context) {
        return;
    }
    Object.assign(context.measurement, values);
}

export function measureSerializerStage<T>(stageName: string, fn: () => T): T {
    const context = currentSerializerMeasurementContext();
    if (!context) {
        return fn();
    }
    const startedAtNs = nowNs();
    try {
        return fn();
    } finally {
        recordSerializerMeasurementStage(stageName, nowNs() - startedAtNs);
    }
}

export function runMeasuredSerializerOperation<T>(
    operation: SerializerMeasurementOperation,
    observer: SerializerMeasurementObserver | undefined,
    seed: Omit<SerializerMeasurement, 'operation' | 'totalDurationNs' | 'stages'>,
    fn: () => T,
): T {
    const measurement: MutableSerializerMeasurement = {
        operation,
        totalDurationNs: 0,
        stages: {},
        ...seed,
    };
    const context: SerializerMeasurementContext = { measurement, observer };
    serializerMeasurementStack.push(context);
    const startedAtNs = nowNs();
    try {
        return fn();
    } finally {
        measurement.totalDurationNs = nowNs() - startedAtNs;
        serializerMeasurementStack.pop();
        observer?.(cloneSerializerMeasurement(measurement));
    }
}
