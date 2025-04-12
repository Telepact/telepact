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

import click
import os
import json
import argparse
import json
import shutil
from typing import cast, Pattern
import jinja2
import click
from pathlib import Path
import re
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


import importlib.resources as pkg_resources
import time
import uvicorn
from .telepact import Client, Server, Message, Serializer, TelepactSchema, MockTelepactSchema, MockServer, SerializationError # Added SerializationError import
import asyncio
import requests

def bump_version(version: str) -> str:
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    return f"{major}.{minor}.{patch}"


def _validate_package(ctx: click.Context, param: click.Parameter, value: str) -> str:
    lang = ctx.params.get('lang')
    if lang == 'java' and not value:
        raise click.BadParameter(
            '--package is required when --lang is java')
    return value


@click.group()
def main() -> None:
    pass


@click.command()
@click.option('--schema-dir', help='telepact schema directory', required=True)
@click.option('--lang', help='Language target (one of "java", "py", or "ts")', required=True)
@click.option('--out', help='Output directory', required=True)
@click.option('--package', help='Java package (use if --lang is "java")', callback=_validate_package)
def codegen(schema_dir: str, lang: str, out: str, package: str) -> None:

    print('Telepact CLI')
    print('Schema directory:', schema_dir)
    print('Language target:', lang)
    print('Output directory:', out)
    if package:
        print('Java package:', package)


    telepact_schema = TelepactSchema.from_directory(schema_dir)

    target = lang
    output_directory = out

    schema_data: list[dict[str, object]] = cast(
        list[dict[str, object]], telepact_schema.original)

    select = telepact_schema.parsed['_ext.Select_']
    possible_fn_selects = select.possible_selects
    possible_fn_selects.pop('fn.ping_', None)
    possible_fn_selects.pop('fn.api_', None)

    # Call the generate function
    _generate_internal(schema_data, possible_fn_selects, target, output_directory, package)


# Define the custom filter
def _regex_replace(s: str, find: str, replace: str) -> str:
    """A custom Jinja2 filter to perform regex replacement."""
    return re.sub(find, replace, s)


def _find_schema_key(schema_data: dict[str, object]) -> str:
    for key in schema_data:
        if key.startswith("struct") or key.startswith("union") or key.startswith("fn") or key.startswith("headers") or key.startswith('info'):
            return key
    raise Exception("No schema key found for " + str(schema_data.keys()))


def _find_tag_key(tag_data: dict[str, object]) -> str:
    for key in tag_data:
        if key != '///':
            return key
    raise Exception("No tag key found")


def _raise_error(message: str) -> None:
    raise Exception(message)


def _generate_internal(schema_data: list[dict[str, object]], possible_fn_selects: dict[str, object], target: str, output_dir: str, java_package: str) -> None:

    # Load jinja template from file
    # Adjust the path to your template directory if necessary
    template_loader = jinja2.PackageLoader(
        'telepact_cli', 'templates')
    template_env = jinja2.Environment(
        loader=template_loader, extensions=['jinja2.ext.do'])

    template_env.filters['regex_replace'] = _regex_replace
    template_env.filters['find_schema_key'] = _find_schema_key
    template_env.filters['find_tag_key'] = _find_tag_key
    template_env.filters['raise_error'] = _raise_error

    if target == "java":

        functions: list[str] = []

        def _write_java_file(jinja_file: str, input: dict, output_file: str) -> None:
            template = template_env.get_template(jinja_file)

            output = template.render(input)

            # Write the output to a file
            if output_dir:
                # Create the Path object for the directory
                output_path = Path(output_dir)

                # Ensure the directory exists
                output_path.mkdir(parents=True, exist_ok=True)

                file_path = output_path / output_file

                # Open the file for writing
                with file_path.open("w") as f:
                    f.write(output)

            else:
                print(output)

        for schema_entry in schema_data:
            schema_key = _find_schema_key(schema_entry)
            if schema_key.startswith('info') or schema_key.startswith('headers'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            _write_java_file('java_type_2.j2', {
                'package': java_package, 'data': schema_entry, 'possible_fn_selects': possible_fn_selects}, f"{schema_key.split('.')[1]}.java")

        _write_java_file('java_server.j2', {
                         'package': java_package, 'functions': functions, 'possible_fn_selects': possible_fn_selects}, f"ServerHandler_.java")

        _write_java_file('java_client.j2', {
                         'package': java_package, 'functions': functions, 'possible_fn_selects': possible_fn_selects}, f"ClientInterface_.java")

        _write_java_file('java_optional.j2', {
                         'package': java_package}, f"Optional_.java")

        _write_java_file('java_utility.j2', {
                         'package': java_package}, f"Utility_.java")

        _write_java_file('typed_message.j2', {
                         'package': java_package}, f"TypedMessage_.java")

        _write_java_file('java_select.j2', {'package': java_package, 'possible_fn_selects': possible_fn_selects}, f"Select_.java")

    elif target == 'py':

        functions = []

        schema_entries: list[dict[str, object]] = []
        for schema_entry in schema_data:
            schema_key = _find_schema_key(schema_entry)
            if schema_key.startswith('info'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            schema_entries.append(schema_entry)

        type_template = template_env.get_template(
            'py_all_2.j2')  # Specify your template file name

        output = type_template.render({
            'input': schema_entries,
            'functions': functions,
            'possible_fn_selects': possible_fn_selects
        })

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            file_path = output_path / f"all_.py"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(output)

            init_file_path = output_path / f"__init__.py"

            with init_file_path.open("w") as f:
                f.write('')

        else:
            print(output)

    elif target == 'ts':

        functions = []

        ts_schema_entries: list[dict[str, object]] = []
        for schema_entry in schema_data:
            schema_key = _find_schema_key(schema_entry)
            if schema_key.startswith('info'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            ts_schema_entries.append(schema_entry)

        ts_type_template = template_env.get_template(
            'ts_all_2.j2')

        output = ts_type_template.render({
            'input': ts_schema_entries,
            'functions': functions,
            'possible_fn_selects': possible_fn_selects
        })

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            file_path = output_path / f"all_.ts"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(output)

        else:
            print(output)


@click.command()
def demo_server() -> None:
    global_variables: dict[str, float] = {}
    global_computations: list[dict[str, object]] = []

    async def handler(message: Message) -> Message:
        nonlocal global_variables, global_computations
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
            return Message({}, {'Ok_': {"tape": global_computations}})

        elif function_name == 'fn.showExample':
            return Message({}, {'Ok_': {'link': {'fn.compute': {'x': {'Constant': {'value': 5}}, 'y': {'Constant': {'value': 7}}, 'op': {'Add': {}}}}}})

        raise Exception(f"Invalid function: {function_name}")


    with pkg_resources.open_text('telepact_cli', 'calculator.telepact.json') as file:
        telepact_json = file.read()

    telepact_schema = TelepactSchema.from_json(telepact_json)

    server_options = Server.Options()
    server_options.auth_required = False
    telepact_server = Server(telepact_schema, handler, server_options)

    print('Server defined')

    async def api_endpoint(request: Request) -> Response:
        request_bytes = await request.body()
        print(f'Request: {request_bytes}')

        # Use the pre-configured telepact_server instance
        response_bytes: bytes = await telepact_server.process(request_bytes)
        print(f'Response: {response_bytes}')

        media_type = 'application/octet-stream' if response_bytes and response_bytes[0] == 0x92 else 'application/json'
        print(f'Media type: {media_type}')

        return Response(content=response_bytes, media_type=media_type)

    routes = [
        Route('/api', endpoint=api_endpoint, methods=['POST']),
    ]

    middleware = [
        Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    ]

    app = Starlette(routes=routes, middleware=middleware)

    uvicorn.run(app, host='0.0.0.0', port=8000)


@click.command()
@click.option('--http-url', help='HTTP URL of a Telepact API', required=False, envvar='TELEPACT_HTTP_URL')
@click.option('--dir', help='Directory of Telepact schemas', required=False, envvar='TELEPACT_DIRECTORY')
@click.option('--generated-collection-length-min', default=0, help='Minimum length of generated collections')
@click.option('--generated-collection-length-max', default=3, help='Maximum length of generated collections')
@click.option('--port', default=8080, help='Port to run the mock server on')
def mock(http_url: str, dir: str, generated_collection_length_min: int, generated_collection_length_max: int, port: int) -> None:
    print(f'http_url: {http_url}')
    print(f'dir: {dir}')
    print(f'generated_collection_length_min: {generated_collection_length_min}')
    print(f'generated_collection_length_max: {generated_collection_length_max}')


    schema: MockTelepactSchema
    if http_url:
        url: str = http_url

        async def adapter(m: Message, s: Serializer) -> Message:
            try:
                request_bytes = s.serialize(m)
            except SerializationError as e:
                # Handle potential serialization errors (e.g., number overflow)
                if isinstance(e.__cause__, OverflowError):
                    # Example: Return a specific Telepact error message
                    # Adjust the error format based on your Telepact schema
                    return Message({}, {"ErrorUnknown_": {"detail": "Input number too large for serialization"}})
                else:
                    # Re-raise other serialization errors
                     return Message({}, {"ErrorUnknown_": {"detail": f"Serialization Error: {e}"}})


            try:
                 # Use a timeout for the request
                response = requests.post(url, data=request_bytes, timeout=10) # 10 second timeout
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                response_bytes = response.content
                response_message = s.deserialize(response_bytes)
                return response_message
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to upstream API: {e}")
                 # Return an appropriate Telepact error message
                 # Adjust the error format based on your Telepact schema
                return Message({}, {"ErrorUpstreamUnavailable_": {"url": url, "error": str(e)}})
            except Exception as e: # Catch potential deserialization errors too
                 print(f"Error processing upstream response: {e}")
                 return Message({}, {"ErrorUnknown_": {"detail": f"Upstream response processing error: {e}"}})


        options = Client.Options()
        telepact_client = Client(adapter, options)

        retries = 3
        response_message = None
        for attempt in range(retries):
            try:
                # Ensure the async function is run correctly
                response_message = asyncio.run(telepact_client.request(Message({}, {'fn.api_': {}})))
                if 'Ok_' in response_message.body or 'Error' in next(iter(response_message.body.keys()), ""): # Check for valid Telepact response structure
                    break
                else:
                     print(f"Attempt {attempt+1}: Received unexpected response structure: {response_message.body}")
                     if attempt < retries - 1: time.sleep(1)

            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(1) # Wait before retrying
                else:
                    # If all retries fail, raise a clearer error
                    raise ConnectionError(f"Failed to connect to Telepact API at {url} after {retries} attempts.") from e

        # Check if we successfully got a response
        if response_message is None:
             raise Exception(f"Could not retrieve API schema from {url}. No valid response received.")

        if 'Ok_' not in response_message.body:
            # Provide more context on failure
            error_key = next(iter(response_message.body.keys()), "UnknownError")
            error_details = response_message.body.get(error_key, {})
            raise Exception(f"Failed to fetch API schema from {url}. Server responded with error: {error_key} - {error_details}")

        api = cast(dict[str, object], response_message.body['Ok_'])['api']
        api_json = json.dumps(api)
        schema = MockTelepactSchema.from_json(api_json)
    elif dir:
        directory: str = dir
        schema = MockTelepactSchema.from_directory(directory)
    else:
        raise click.BadParameter('Either --http-url or --dir must be provided.')

    print('Telepact JSON loaded for mock server:')
    # print(json.dumps(schema.original, indent=4)) # Optionally print the schema

    mock_server_options = MockServer.Options()
    mock_server_options.generated_collection_length_min = generated_collection_length_min
    mock_server_options.generated_collection_length_max = generated_collection_length_max
    mock_server = MockServer(schema, mock_server_options)

    async def mock_api_endpoint(request: Request) -> Response:
        request_bytes = await request.body()
        response_bytes = await mock_server.process(request_bytes)
        media_type = 'application/octet-stream' if response_bytes and response_bytes[0] == 0x92 else 'application/json'
        return Response(content=response_bytes, media_type=media_type)

    routes = [
        Route('/api', endpoint=mock_api_endpoint, methods=['POST']),
    ]

    middleware = [
        Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    ]

    app = Starlette(routes=routes, middleware=middleware)

    print(f"Starting mock server on port {port}...")
    uvicorn.run(app, host='0.0.0.0', port=port)

main.add_command(codegen)
main.add_command(demo_server)
main.add_command(mock)

if __name__ == "__main__":
    main()