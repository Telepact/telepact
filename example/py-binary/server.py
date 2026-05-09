#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from telepact import FunctionRouter, Message, Server, TelepactSchema, TelepactSchemaFiles


async def get_numbers(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    limit = argument['limit']
    return Message({}, {
        'Ok_': {
            'values': list(range(1, limit + 1)),
        },
    })


def build_telepact_server() -> Server:
    files = TelepactSchemaFiles('api')
    schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
    options = Server.Options()
    options.auth_required = False
    function_router = FunctionRouter({'fn.getNumbers': get_numbers})
    return Server(schema, function_router, options)
