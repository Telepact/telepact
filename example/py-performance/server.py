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

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles


def _build_catalog(item_count: int, profile: str) -> dict[str, object]:
    items: list[dict[str, object]] = []
    tag_count = 0
    revision_count = 0

    for i in range(item_count):
        tags = [
            f'tag-{i % 7}',
            f'cohort-{i % 5}',
            f'release-{(i // 3) % 4}',
        ]
        revisions = [
            {
                'version': 1,
                'changedBy': 'telepact-bot',
                'note': f'bootstrap-{i % 11}',
                'approved': True,
            },
            {
                'version': 2,
                'changedBy': f'editor-{i % 9}',
                'note': f'price-adjustment-{i % 13}',
                'approved': (i % 4) != 0,
            },
            {
                'version': 3,
                'changedBy': f'qa-{i % 6}',
                'note': f'validation-pass-{i % 17}',
                'approved': True,
            },
        ]
        tag_count += len(tags)
        revision_count += len(revisions)
        items.append({
            'id': i + 1,
            'sku': f'SKU-{i + 1:05d}',
            'title': f'{profile.title()} item {i + 1}',
            'category': f'category-{i % 8}',
            'priceCents': 1_000 + ((i * 37) % 2_500),
            'available': (i % 6) != 0,
            'warehouse': {
                'region': f'region-{i % 4}',
                'aisle': f'A-{i % 16}',
                'bin': f'BIN-{i % 32:02d}',
            },
            'analytics': {
                'views': 1_000 + (i * 19),
                'purchases': 20 + (i % 40),
                'returns': i % 5,
            },
            'tags': tags,
            'revisions': revisions,
        })

    return {
        'summary': {
            'profile': profile,
            'itemCount': item_count,
            'tagCount': tag_count,
            'revisionCount': revision_count,
        },
        'generatedAt': '2026-05-01T00:00:00Z',
        'items': items,
    }


SMALL_CATALOG = _build_catalog(3, 'small')
BIG_CATALOG = _build_catalog(250, 'big')


async def get_catalog(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    profile = argument['profile']
    if profile == 'small':
        payload = SMALL_CATALOG
    elif profile == 'big':
        payload = BIG_CATALOG
    else:
        payload = {
            'summary': {
                'profile': str(profile),
                'itemCount': 0,
                'tagCount': 0,
                'revisionCount': 0,
            },
            'generatedAt': '2026-05-01T00:00:00Z',
            'items': [],
        }

    return Message({}, {'Ok_': payload})


def build_telepact_server() -> Server:
    files = TelepactSchemaFiles('api')
    schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
    options = Server.Options()
    options.auth_required = False
    function_router = FunctionRouter({'fn.getCatalog': get_catalog})
    return Server(schema, function_router, options)
