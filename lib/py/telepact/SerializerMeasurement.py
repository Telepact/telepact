#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
import time
from typing import Callable


@dataclass
class SerializerMeasurementStageStats:
    total_duration_ns: int
    count: int


@dataclass
class SerializerMeasurement:
    operation: str
    total_duration_ns: int
    binary_requested: bool
    transport_encoding: str
    protocol_encoding: str
    packed: bool
    fell_back_to_json: bool
    stages: dict[str, SerializerMeasurementStageStats] = field(default_factory=dict)


SerializerMeasurementObserver = Callable[[SerializerMeasurement], None]


@dataclass
class _SerializerMeasurementContext:
    measurement: SerializerMeasurement
    observer: SerializerMeasurementObserver | None


_SERIALIZER_MEASUREMENT_CONTEXT: ContextVar[_SerializerMeasurementContext | None] = ContextVar(
    "_SERIALIZER_MEASUREMENT_CONTEXT",
    default=None,
)


def _clone_serializer_measurement(measurement: SerializerMeasurement) -> SerializerMeasurement:
    return SerializerMeasurement(
        operation=measurement.operation,
        total_duration_ns=measurement.total_duration_ns,
        binary_requested=measurement.binary_requested,
        transport_encoding=measurement.transport_encoding,
        protocol_encoding=measurement.protocol_encoding,
        packed=measurement.packed,
        fell_back_to_json=measurement.fell_back_to_json,
        stages={
            stage_name: SerializerMeasurementStageStats(
                total_duration_ns=stats.total_duration_ns,
                count=stats.count,
            )
            for stage_name, stats in measurement.stages.items()
        },
    )


def serializer_measurement_to_dict(measurement: SerializerMeasurement) -> dict[str, object]:
    return {
        "operation": measurement.operation,
        "totalDurationNs": measurement.total_duration_ns,
        "binaryRequested": measurement.binary_requested,
        "transportEncoding": measurement.transport_encoding,
        "protocolEncoding": measurement.protocol_encoding,
        "packed": measurement.packed,
        "fellBackToJson": measurement.fell_back_to_json,
        "stages": {
            stage_name: {
                "totalDurationNs": stats.total_duration_ns,
                "count": stats.count,
            }
            for stage_name, stats in measurement.stages.items()
        },
    }


def annotate_serializer_measurement(**values: object) -> None:
    context = _SERIALIZER_MEASUREMENT_CONTEXT.get()
    if context is None:
        return
    for key, value in values.items():
        setattr(context.measurement, key, value)


def measure_serializer_stage(stage_name: str, fn: Callable[[], object]):
    context = _SERIALIZER_MEASUREMENT_CONTEXT.get()
    if context is None:
        return fn()
    started_at_ns = time.perf_counter_ns()
    try:
        return fn()
    finally:
        duration_ns = time.perf_counter_ns() - started_at_ns
        existing = context.measurement.stages.get(stage_name)
        if existing is None:
            context.measurement.stages[stage_name] = SerializerMeasurementStageStats(
                total_duration_ns=duration_ns,
                count=1,
            )
        else:
            existing.total_duration_ns += duration_ns
            existing.count += 1


def run_measured_serializer_operation(
    operation: str,
    observer: SerializerMeasurementObserver | None,
    *,
    binary_requested: bool,
    transport_encoding: str,
    protocol_encoding: str,
    packed: bool,
    fell_back_to_json: bool,
    fn: Callable[[], object],
):
    measurement = SerializerMeasurement(
        operation=operation,
        total_duration_ns=0,
        binary_requested=binary_requested,
        transport_encoding=transport_encoding,
        protocol_encoding=protocol_encoding,
        packed=packed,
        fell_back_to_json=fell_back_to_json,
    )
    token = _SERIALIZER_MEASUREMENT_CONTEXT.set(_SerializerMeasurementContext(measurement, observer))
    started_at_ns = time.perf_counter_ns()
    try:
        return fn()
    finally:
        measurement.total_duration_ns = time.perf_counter_ns() - started_at_ns
        _SERIALIZER_MEASUREMENT_CONTEXT.reset(token)
        if observer is not None:
            observer(_clone_serializer_measurement(measurement))
