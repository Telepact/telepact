import click
import os
from lxml import etree as ET
import json
import toml
import yaml
import argparse
import json
import shutil
from typing import cast, Pattern
import jinja2
import click
from pathlib import Path
import re
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import importlib.resources as pkg_resources
import time
import uvicorn
from .msgpact import Server, Message, MsgPactSchema, MockMsgPactSchema, MockServer
import pprint


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
@click.option('--schema-dir', help='msgPact schema directory', required=True)
@click.option('--lang', help='Language target (one of "java", "py", or "ts")', required=True)
@click.option('--out', help='Output directory', required=True)
@click.option('--package', help='Java package (use if --lang is "java")', callback=_validate_package)
def codegen(schema_dir: str, lang: str, out: str, package: str) -> None:

    print('MsgPact CLI')
    print('Schema directory:', schema_dir)
    print('Language target:', lang)
    print('Output directory:', out)
    if package:
        print('Java package:', package)


    msgpact_schema = MsgPactSchema.from_directory(schema_dir)

    target = lang
    output_directory = out

    schema_data: list[dict[str, object]] = cast(
        list[dict[str, object]], msgpact_schema.original)

    # Call the generate function
    _generate_internal(schema_data, target, output_directory, package)


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


def _generate_internal(schema_data: list[dict[str, object]], target: str, output_dir: str, java_package: str) -> None:

    # Load jinja template from file
    # Adjust the path to your template directory if necessary
    template_loader = jinja2.PackageLoader(
        'msgpact_cli', 'templates')
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
                'package': java_package, 'data': schema_entry}, f"{schema_key.split('.')[1]}.java")

        _write_java_file('java_server.j2', {
                         'package': java_package, 'functions': functions}, f"ServerHandler_.java")

        _write_java_file('java_client.j2', {
                         'package': java_package, 'functions': functions}, f"ClientInterface_.java")

        _write_java_file('java_optional.j2', {
                         'package': java_package}, f"Optional_.java")

        _write_java_file('java_utility.j2', {
                         'package': java_package}, f"Utility_.java")

        _write_java_file('typed_message.j2', {
                         'package': java_package}, f"TypedMessage_.java")

    elif target == 'py':

        functions = []

        schema_entries: list[dict[str, object]] = []
        for schema_entry in schema_data:
            schema_key = _find_schema_key(schema_entry)
            if schema_key.startswith('info') or schema_key.startswith('requestHeader') or schema_key.startswith('responseHeader'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            schema_entries.append(schema_entry)

        type_template = template_env.get_template(
            'py_all_2.j2')  # Specify your template file name

        output = type_template.render({
            'input': schema_entries,
            'functions': functions
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
            if schema_key.startswith('info') or schema_key.startswith('requestHeader') or schema_key.startswith('responseHeader'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            ts_schema_entries.append(schema_entry)

        ts_type_template = template_env.get_template(
            'ts_all_2.j2')

        output = ts_type_template.render({
            'input': ts_schema_entries,
            'functions': functions
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
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Any origin
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
    with pkg_resources.open_text('msgpact_cli', 'calculator.msgpact.json') as file:
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

    uvicorn.run(app, host='0.0.0.0', port=8000)


@click.command()
@click.option('--http-url', help='HTTP URL of a MsgPact API', required=False, envvar='MSGPACT_HTTP_URL')
@click.option('--dir', help='Directory of MsgPact schemas', required=False, envvar='MSGPACT_DIRECTORY')
def mock(http_url: str, dir: str) -> None:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Any origin
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    if http_url:
        url: str = http_url

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
        msgpact_client = Client(adapter, options)

        retries = 3
        for attempt in range(retries):
            try:
                response_message = asyncio.run(msgpact_client.request(Message({}, {'fn.api_': {}})))
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    raise e

        if 'Ok_' not in response_message.body:
            raise Exception("Invalid url: " + str(response_message))
        api = cast(dict[str, object], response_message.body['Ok_'])['api']
        api_json = json.dumps(api)
        schema = MockMsgPactSchema.from_json(api_json)
    elif dir:
        directory: str = dir
        schema = MockMsgPactSchema.from_directory(directory)
    else:
        raise click.BadParameter('Either --http-url or --dir must be provided.')

    print('msgPact JSON:')
    print(json.dumps(schema.original, indent=4))

    mock_server_options = MockServer.Options()
    mock_server = MockServer(schema, mock_server_options)

    @app.post('/api')
    async def api(request: Request) -> Response:
        request_bytes = await request.body()
        response_bytes = await mock_server.process(request_bytes)
        media_type = 'application/octet-stream' if response_bytes[0] == 0x92 else 'application/json'
        return Response(content=response_bytes, media_type=media_type)

    uvicorn.run(app, host='0.0.0.0', port=8080)

main.add_command(codegen)
main.add_command(demo_server)
main.add_command(mock)

if __name__ == "__main__":
    main()
