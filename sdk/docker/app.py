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

from typing import Tuple, cast
from fastapi import FastAPI, Request
from telepact.TelepactSchema import TelepactSchema
from telepact.Client import Client
from telepact.Message import Message
from telepact.Serializer import Serializer
from telepact.SerializationError import SerializationError
from telepact.MockServer import MockServer
from telepact.MockTelepactSchema import MockTelepactSchema
import asyncio
import json
import os
import requests
from fastapi.responses import Response
from fastapi import FastAPI, Query, Request


app = FastAPI()

global mock_server


@app.post('/api')
async def post_endpoint(request: Request) -> Response:
    request_bytes = await request.body()
    # Process the data and request_bytes as needed

    response_bytes = await mock_server.process(request_bytes)

    media_type = 'application/octet-stream' if response_bytes[0] == 0x92 else 'application/json'

    return Response(content=response_bytes, media_type=media_type)


@app.on_event('startup')
async def startup_event():
    telepact_url_env_var_is_set = 'TELEPACT_URL' in os.environ

    def get_telepact_url_env_var() -> str:
        return os.environ['TELEPACT_URL']

    telepact_directory_env_var_is_set = 'TELEPACT_DIRECTORY' in os.environ

    def get_telepact_directory_env_var() -> str:
        return os.environ['TELEPACT_DIRECTORY']

    if telepact_url_env_var_is_set:
        url: str = get_telepact_url_env_var()

        async def adapter(m: Message, s: Serializer) -> Message:
            try:
                request_bytes = s.serialize(m)
            except SerializationError as e:
                if isinstance(e.__context__, OverflowError):
                    return Message({"numberTooBig": True}, {"ErrorUnknown_": {}})
                else:
                    raise

            response = requests.post(url, data=request_bytes)
            response_bytes = response.content

            response_message = s.deserialize(response_bytes)
            return response_message

        options = Client.Options()

        telepact_client = Client(adapter, options)

        retries = 3
        for attempt in range(retries):
            try:
                response_message = await telepact_client.request(Message({}, {'fn.api_': {}}))
                break
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise e

        if 'Ok_' not in response_message.body:
            raise Exception("Invalid url: " + str(response_message))
        api = cast(dict[str, object], response_message.body['Ok_'])['api']

        api_json = json.dumps(api)

        schema = MockTelepactSchema.from_json(api_json)
    elif telepact_directory_env_var_is_set:
        directory: str = get_telepact_directory_env_var()
        schema = MockTelepactSchema.from_directory(directory)

    print('telepact JSON:')
    print(schema.original)

    mock_server_options = MockServer.Options()
    global mock_server
    mock_server = MockServer(schema, mock_server_options)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)
