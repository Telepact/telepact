from typing import Tuple, cast
from fastapi import FastAPI, Request
from uapi.UApiSchema import UApiSchema
from uapi.Client import Client
from uapi.Message import Message
from uapi.Serializer import Serializer
from uapi.SerializationError import SerializationError
from uapi.MockServer import MockServer
from uapi.MockUApiSchema import MockUApiSchema
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
    uapi_url_env_var_is_set = 'UAPI_URL' in os.environ

    def get_uapi_url_env_var() -> str:
        return os.environ['UAPI_URL']

    uapi_directory_env_var_is_set = 'UAPI_DIRECTORY' in os.environ

    def get_uapi_directory_env_var() -> str:
        return os.environ['UAPI_DIRECTORY']

    if uapi_url_env_var_is_set:
        url: str = get_uapi_url_env_var()

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

        uapi_client = Client(adapter, options)

        retries = 3
        for attempt in range(retries):
            try:
                response_message = await uapi_client.request(Message({}, {'fn.api_': {}}))
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

        schema = MockUApiSchema.from_json(api_json)
    elif uapi_directory_env_var_is_set:
        directory: str = get_uapi_directory_env_var()
        schema = MockUApiSchema.from_directory(directory)

    mock_server_options = MockServer.Options()
    global mock_server
    mock_server = MockServer(schema, mock_server_options)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)