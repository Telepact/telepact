from fastapi import FastAPI, Query, Request
from typing import Dict, Tuple, cast
from msgpact import Server, Message, MsgPactSchema
import importlib.resources as pkg_resources
import time
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import sys
import os

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


async def handler(message: Message) -> Message:
    global global_variables
    function_name = next(iter(message.body.keys()))
    arguments: dict[str, object] = cast(
        dict[str, object], message.body[function_name])

    if function_name == 'fn.compute':
        x = cast(dict[str, object], arguments['x'])
        y = cast(dict[str, object], arguments['y'])
        op = cast(dict[str, object], arguments['op'])

        # Extract values
        x_value = cast(float, cast(dict[str, object], x['Constant'])[
            'value']) if 'Constant' in x else global_variables.get(cast(str, cast(dict[str, object], x['Variable'])['name']), 0)
        y_value = cast(float, cast(dict[str, object], y['Constant'])[
            'value']) if 'Constant' in y else global_variables.get(cast(str, cast(dict[str, object], y['Variable'])['name']), 0)

        if x_value is None or y_value is None:
            raise Exception("Invalid input")

        # Perform operation
        if 'Add' in op:
            result = x_value + y_value
        elif 'Sub' in op:
            result = x_value - y_value
        elif 'Mul' in op:
            result = x_value * y_value
        elif 'Div' in op:
            if y_value == 0:
                return Message({}, {"ErrorCannotDivideByZero": {}})
            result = x_value / y_value
        else:
            raise Exception("Invalid operation")

        # Log computation
        global_computations.append({
            "firstOperand": x,
            "secondOperand": y,
            "operation": op,
            "timestamp": int(time.time()),
            "successful": True
        })

        return Message({}, {'Ok_': {"result": result}})

    elif function_name == 'fn.saveVariables':
        these_variables = cast(dict[str, float], arguments['variables'])

        global_variables.update(these_variables)

        return Message({}, {'Ok_': {}})

    elif function_name == 'fn.exportVariables':
        limit = cast(int, arguments.get('limit', 10))

        variables = [{"name": k, "value": v}
                     for k, v in global_variables.items()]
        if limit:
            variables = variables[:limit]
        return Message({}, {'Ok_': {"variables": variables}})

    elif function_name == 'fn.getPaperTape':
        # Assuming computations are stored in a global list
        return Message({}, {'Ok_': {"tape": global_computations}})

    elif function_name == 'fn.showExample':
        return Message({}, {'Ok_': {'link': {'fn.compute': {'x': {'Constant': {'value': 5}}, 'y': {'Constant': {'value': 7}}, 'op': {'Add': {}}}}}})

    raise Exception("Invalid function")

# Load json from file
with pkg_resources.open_text('calculator_service', 'calculator.msgpact.json') as file:
    msgpact_json = file.read()

msgpact_schema = MsgPactSchema.from_json(msgpact_json)

server_options = Server.Options()
server_options.auth_required = False
server = Server(msgpact_schema, handler, server_options)

print('Server defined')

global_variables: dict[str, float] = {}
global_computations: list[dict[str, object]] = []


@app.post('/api')
async def api(request: Request) -> Response:
    request_bytes = await request.body()

    print(f'Request: {request_bytes}')

    response_bytes: bytes = await server.process(request_bytes)

    print(f'Response: {response_bytes}')

    media_type = 'application/octet-stream' if response_bytes[0] == 0x92 else 'application/json'

    print(f'Media type: {media_type}')

    return Response(content=response_bytes, media_type=media_type)


def run_main():
    uvicorn.run("calculator_service.__main__:app",
                host='0.0.0.0', port=8000, reload=True)


if __name__ == "__main__":
    run_main()
