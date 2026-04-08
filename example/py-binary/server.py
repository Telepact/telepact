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

from telepact import Message, Server, TelepactSchema, TelepactSchemaFiles


files = TelepactSchemaFiles('api')
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()
options.auth_required = False


async def get_numbers(function_name: str, request_message: Message) -> Message:
    argument = request_message.body[function_name]
    limit = argument['limit']
    return Message({}, {
        'Ok_': {
            'values': list(range(1, limit + 1)),
        },
    })


def build_telepact_server() -> Server:
    return Server(schema, {'fn.getNumbers': get_numbers}, options)
