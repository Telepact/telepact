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

from pathlib import Path

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles

SCALARS = [
    'value01',
    'value02',
    'value03',
    'value04',
    'value05',
    'value06',
    'value07',
    'value08',
    'value09',
    'value10',
    'value11',
    'value12',
]

SIZE_CONFIG = {
    'small': {
        'digit_offset': 10,
        'string_repeat': 1,
        'row_count': 10,
        'order_count': 3,
        'lines_per_order': 2,
        'alert_count': 2,
        'activity_count': 5,
        'narrative_repeat': 3,
    },
    'big': {
        'digit_offset': 10_000,
        'string_repeat': 8,
        'row_count': 120,
        'order_count': 18,
        'lines_per_order': 5,
        'alert_count': 10,
        'activity_count': 45,
        'narrative_repeat': 18,
    },
}


def _get_size_config(size: str) -> dict[str, int]:
    if size not in SIZE_CONFIG:
        raise ValueError(f'Unsupported size: {size}')
    return SIZE_CONFIG[size]


def _build_flat_numbers(size: str) -> dict[str, float]:
    cfg = _get_size_config(size)
    digit_offset = cfg['digit_offset']
    return {
        field: float(digit_offset * (index + 1) + (index / 10))
        for index, field in enumerate(SCALARS)
    }


def _build_flat_strings(size: str) -> dict[str, str]:
    cfg = _get_size_config(size)
    repeat = cfg['string_repeat']
    return {
        field: f'{field}-' + ('payload-segment-' * repeat) + str(index)
        for index, field in enumerate(SCALARS)
    }


def _build_record_batch(size: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    cfg = _get_size_config(size)
    rows: list[dict[str, object]] = []
    total_score = 0.0
    active_rows = 0
    for index in range(cfg['row_count']):
        active = index % 3 != 0
        score = round((index + 1) * 1.75, 2)
        total_score += score
        if active:
            active_rows += 1
        rows.append({
            'recordId': f'row-{size}-{index:04d}',
            'group': f'group-{index % 7}',
            'owner': f'owner-{index % 11}',
            'status': ['new', 'ready', 'done'][index % 3],
            'score': score,
            'quantity': (index % 9) + 1,
            'active': active,
            'note': ('batched record payload ' * cfg['string_repeat']).strip(),
        })

    summary = {
        'totalRows': len(rows),
        'activeRows': active_rows,
        'totalScore': round(total_score, 2),
        'averageScore': round(total_score / len(rows), 2),
    }
    return rows, summary


def _build_dashboard(size: str) -> dict[str, object]:
    cfg = _get_size_config(size)
    orders = []
    for order_index in range(cfg['order_count']):
        lines = []
        subtotal = 0.0
        for line_index in range(cfg['lines_per_order']):
            unit_price = round(19.5 + order_index + (line_index * 0.75), 2)
            quantity = (line_index % 4) + 1
            discount_rate = round((line_index % 3) * 0.05, 2)
            subtotal += unit_price * quantity
            lines.append({
                'sku': f'SKU-{order_index:03d}-{line_index:02d}',
                'quantity': quantity,
                'unitPrice': unit_price,
                'discountRate': discount_rate,
            })
        orders.append({
            'orderId': f'order-{size}-{order_index:04d}',
            'status': ['draft', 'paid', 'fulfilled', 'delayed'][order_index % 4],
            'shippingCity': ['Seattle', 'London', 'Tokyo', 'Berlin'][order_index % 4],
            'subtotal': round(subtotal, 2),
            'total': round(subtotal * 1.08, 2),
            'lines': lines,
        })

    alerts = [{
        'code': f'ALERT-{alert_index:03d}',
        'severity': ['info', 'warning', 'critical'][alert_index % 3],
        'owner': f'oncall-{alert_index % 4}',
        'message': ('backend queue depth increased ' * cfg['string_repeat']).strip(),
        'acknowledged': alert_index % 2 == 0,
    } for alert_index in range(cfg['alert_count'])]

    activity = [{
        'at': f'2026-05-09T12:{event_index % 60:02d}:00Z',
        'actor': f'user-{event_index % 17}',
        'action': ['login', 'edit', 'approve', 'export'][event_index % 4],
        'target': f'resource-{event_index % 9}',
        'durationMs': 20 + (event_index % 7) * 11,
    } for event_index in range(cfg['activity_count'])]

    return {
        'profile': {
            'accountId': f'account-{size}-042',
            'plan': 'enterprise',
            'region': 'us-west-2',
            'orgName': 'Ada Analytics',
            'accountManager': 'Morgan Singh',
            'supportTier': 'platinum',
        },
        'orders': orders,
        'alerts': alerts,
        'activity': activity,
        'metrics': {
            'monthlySpend': round(38_400.25 + cfg['order_count'] * 17.2, 2),
            'openInvoices': cfg['alert_count'] + 2,
            'activeUsers': cfg['activity_count'] * 3,
            'latencyP50Ms': 18.4,
            'latencyP95Ms': 42.7 + cfg['string_repeat'],
        },
        'narrative': ('This dashboard payload is intentionally verbose. ' * cfg['narrative_repeat']).strip(),
        'generatedAt': '2026-05-09T12:00:00Z',
    }


async def get_flat_numbers(function_name: str, request_message: Message) -> Message:
    size = request_message.body[function_name]['size']
    return Message({}, {'Ok_': {'value': _build_flat_numbers(size)}})


async def get_flat_strings(function_name: str, request_message: Message) -> Message:
    size = request_message.body[function_name]['size']
    return Message({}, {'Ok_': {'value': _build_flat_strings(size)}})


async def get_record_batch(function_name: str, request_message: Message) -> Message:
    size = request_message.body[function_name]['size']
    rows, summary = _build_record_batch(size)
    return Message({}, {'Ok_': {'rows': rows, 'summary': summary}})


async def get_dashboard(function_name: str, request_message: Message) -> Message:
    size = request_message.body[function_name]['size']
    return Message({}, {'Ok_': _build_dashboard(size)})


def build_telepact_server() -> Server:
    api_dir = Path(__file__).resolve().parent / 'api'
    files = TelepactSchemaFiles(str(api_dir))
    schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
    options = Server.Options()
    options.auth_required = False
    function_router = FunctionRouter({
        'fn.getFlatNumbers': get_flat_numbers,
        'fn.getFlatStrings': get_flat_strings,
        'fn.getRecordBatch': get_record_batch,
        'fn.getDashboard': get_dashboard,
    })
    return Server(schema, function_router, options)
