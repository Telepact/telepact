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

import asyncio
import json

from telepact import FunctionRouter, Message, Server, TelepactSchema


async def _get_nested(function_name: str, request_message: Message) -> Message:
    return Message({}, {
        'Ok_': {
            'cards': [
                {
                    'title': 'Ship docs',
                    'done!': False,
                    'owner': {
                        'id': 'user-1',
                        'name': 'Ada',
                        'email': 'ada@example.com',
                    },
                },
            ],
            'item': {
                'Card': {
                    'card': {
                        'title': 'Ship docs',
                        'done!': False,
                        'owner': {
                            'id': 'user-1',
                            'name': 'Ada',
                            'email': 'ada@example.com',
                        },
                    },
                    'summary': 'ready',
                },
            },
            'ownerMap!': {
                'primary': {
                    'id': 'user-2',
                    'name': 'Grace',
                    'email': 'grace@example.com',
                },
            },
        },
    })


def test_select_applies_to_nested_structs_unions_arrays_and_objects() -> None:
    schema = TelepactSchema.from_json(json.dumps([
        {
            'struct.Profile': {
                'id': 'string',
                'name': 'string',
                'email': 'string',
            },
        },
        {
            'struct.ResultCard': {
                'title': 'string',
                'done!': 'boolean',
                'owner': 'struct.Profile',
            },
        },
        {
            'union.ResultItem': [
                {
                    'Card': {
                        'card': 'struct.ResultCard',
                        'summary': 'string',
                    },
                },
                {
                    'Note': {
                        'body': 'string',
                    },
                },
            ],
        },
        {
            'fn.getNested': {},
            '->': [
                {
                    'Ok_': {
                        'cards': ['struct.ResultCard'],
                        'item': 'union.ResultItem',
                        'ownerMap!': {'string': 'struct.Profile'},
                    },
                },
            ],
        },
    ]))
    options = Server.Options()
    options.auth_required = False
    server = Server(schema, FunctionRouter({'fn.getNested': _get_nested}), options)

    response = asyncio.run(server.process(json.dumps([
        {
            '@select_': {
                '->': {
                    'Ok_': ['cards', 'item', 'ownerMap!'],
                },
                'struct.ResultCard': ['title', 'owner'],
                'struct.Profile': ['id'],
                'union.ResultItem': {
                    'Card': ['card'],
                },
            },
        },
        {
            'fn.getNested': {},
        },
    ]).encode()))

    assert json.loads(response.bytes) == [
        {},
        {
            'Ok_': {
                'cards': [
                    {
                        'title': 'Ship docs',
                        'owner': {
                            'id': 'user-1',
                        },
                    },
                ],
                'item': {
                    'Card': {
                        'card': {
                            'title': 'Ship docs',
                            'owner': {
                                'id': 'user-1',
                            },
                        },
                    },
                },
                'ownerMap!': {
                    'primary': {
                        'id': 'user-2',
                    },
                },
            },
        },
    ]
