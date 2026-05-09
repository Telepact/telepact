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

import hashlib
from dataclasses import dataclass

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles


@dataclass(frozen=True)
class PayloadShapeConfig:
    count: int
    nested_count: int


_SIZE_CONFIGS: dict[str, PayloadShapeConfig] = {
    'small': PayloadShapeConfig(count=6, nested_count=3),
    'big': PayloadShapeConfig(count=96, nested_count=8),
}


def _repeat_text(seed: str, length: int) -> str:
    block = f'{seed}-telepact-performance-'
    repeats = (length // len(block)) + 1
    return (block * repeats)[:length]


def _build_typical_payload(size: str) -> dict[str, object]:
    config = _SIZE_CONFIGS[size]
    shipments: list[dict[str, object]] = []
    for shipment_index in range(config.count):
        items: list[dict[str, object]] = []
        for item_index in range(config.nested_count):
            items.append({
                'sku': f'SKU-{shipment_index:03d}-{item_index:02d}',
                'quantity': (item_index % 5) + 1,
                'priceCents': 2499 + (shipment_index * 7) + item_index,
                'fragile': (shipment_index + item_index) % 3 == 0,
                'warehouse': f'WH-{shipment_index % 4}',
                'tags': [
                    f'tag-{shipment_index % 5}',
                    f'zone-{item_index % 3}',
                    f'carrier-{(shipment_index + item_index) % 4}',
                ],
            })
        shipments.append({
            'shipmentId': f'SHP-{shipment_index:04d}',
            'customerId': f'CUST-{shipment_index % 23:03d}',
            'priority': 'express' if shipment_index % 4 == 0 else 'standard',
            'address': {
                'name': f'Customer {shipment_index}',
                'street': f'{100 + shipment_index} Market Street',
                'city': 'San Francisco' if shipment_index % 2 == 0 else 'New York',
                'region': 'CA' if shipment_index % 2 == 0 else 'NY',
                'postalCode': f'{94000 + shipment_index:05d}',
                'country': 'US',
            },
            'items': items,
            'note': _repeat_text(f'note-{shipment_index}', 48),
            'etaDays': (shipment_index % 7) + 1,
            'riskScore': round(0.25 + ((shipment_index % 17) / 19), 6),
        })
    return {
        'Typical': {
            'shipments': shipments,
            'eventNotes': [_repeat_text(f'event-{index}', 36) for index in range(config.count)],
            'flags': {
                'containsFragile': True,
                'requiresSignature': True,
                'crossDocked': size == 'big',
            },
        },
    }


def _build_string_heavy_payload(size: str) -> dict[str, object]:
    config = _SIZE_CONFIGS[size]
    rows = []
    for row_index in range(config.count * 4):
        rows.append({
            'id': f'row-{row_index:04d}',
            'group': f'group-{row_index % 9}',
            'locale': ['en-US', 'en-GB', 'fr-FR', 'de-DE'][row_index % 4],
            'title': _repeat_text(f'title-{row_index}', 32),
            'summary': _repeat_text(f'summary-{row_index}', 96),
            'body': _repeat_text(f'body-{row_index}', 180 if size == 'big' else 72),
            'tag': f'tag-{row_index % 11}',
            'slug': _repeat_text(f'slug-{row_index}', 24),
        })
    return {
        'StringHeavy': {
            'rows': rows,
            'locales': ['en-US', 'en-GB', 'fr-FR', 'de-DE', 'es-ES'],
            'category': 'documentation-snippets',
        },
    }


def _build_number_heavy_payload(size: str) -> dict[str, object]:
    config = _SIZE_CONFIGS[size]
    rows = []
    total_rows = config.count * 5
    for row_index in range(total_rows):
        base = (row_index + 1) * 1.125
        rows.append({
            'id': row_index + 1,
            'metricA': round(base, 6),
            'metricB': round(base * 1.5, 6),
            'metricC': round(base * 2.25, 6),
            'metricD': round(base * 3.5, 6),
            'metricE': round(base * 5.25, 6),
            'metricF': round(base * 8.0, 6),
            'metricG': round(base * 13.0, 6),
        })
    return {
        'NumberHeavy': {
            'rows': rows,
            'totals': {
                'metricA': round(sum(row['metricA'] for row in rows), 6),
                'metricB': round(sum(row['metricB'] for row in rows), 6),
                'metricC': round(sum(row['metricC'] for row in rows), 6),
                'metricD': round(sum(row['metricD'] for row in rows), 6),
            },
            'sampleRateHz': 240 if size == 'big' else 60,
        },
    }


def build_payload(profile: str, size: str) -> dict[str, object]:
    if profile == 'typical':
        return _build_typical_payload(size)
    if profile == 'strings':
        return _build_string_heavy_payload(size)
    if profile == 'numbers':
        return _build_number_heavy_payload(size)
    raise ValueError(f'unsupported profile: {profile}')


def build_summary(profile: str, size: str, payload: dict[str, object]) -> dict[str, object]:
    config = _SIZE_CONFIGS[size]
    record_count = 0
    scalar_count = 0
    approx_characters = 0

    if profile == 'typical':
        shipments = payload['Typical']['shipments']
        record_count = len(shipments)
        scalar_count = len(shipments) * (8 + (config.nested_count * 6))
        approx_characters = len(shipments) * (180 + (config.nested_count * 32))
    elif profile == 'strings':
        rows = payload['StringHeavy']['rows']
        record_count = len(rows)
        scalar_count = len(rows) * 8
        approx_characters = len(rows) * (420 if size == 'big' else 220)
    elif profile == 'numbers':
        rows = payload['NumberHeavy']['rows']
        record_count = len(rows)
        scalar_count = len(rows) * 8
        approx_characters = len(rows) * 12

    return {
        'recordCount': record_count,
        'scalarCount': scalar_count,
        'approxCharacters': approx_characters,
        'hint': f'{profile}:{size}',
    }


async def get_benchmark_payload(_function_name: str, request_message: Message) -> Message:
    arguments = request_message.body['fn.getBenchmarkPayload']
    profile = arguments['profile']
    size = arguments['size']
    payload = build_payload(profile, size)
    summary = build_summary(profile, size, payload)
    checksum_source = f'{profile}:{size}:{summary["recordCount"]}:{summary["scalarCount"]}'
    checksum = hashlib.sha256(checksum_source.encode('utf-8')).hexdigest()[:16]
    return Message({}, {
        'Ok_': {
            'profile': profile,
            'size': size,
            'summary': summary,
            'payload': payload,
            'checksum': checksum,
        },
    })


def build_telepact_server() -> Server:
    files = TelepactSchemaFiles('api')
    schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
    options = Server.Options()
    options.auth_required = False
    function_router = FunctionRouter({'fn.getBenchmarkPayload': get_benchmark_payload})
    return Server(schema, function_router, options)
