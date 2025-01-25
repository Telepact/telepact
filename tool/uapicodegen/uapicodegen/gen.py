import argparse
import json
import shutil
from typing import cast, Pattern
import jinja2
import click
from pathlib import Path
import re


def _validate_package(ctx: click.Context, param: click.Parameter, value: str) -> str:
    lang = ctx.params.get('lang')
    if lang == 'java' and not value:
        raise click.BadParameter(
            '--package is required when --lang is java')
    return value


@click.command()
@click.option('--schema', help='uAPI schema', required=True)
@click.option('--lang', help='Language target', required=True)
@click.option('--out', help='Output directory', required=True)
@click.option('--package', help='Java package', callback=_validate_package)
def generate(schema: str, lang: str, out: str, package: str) -> None:

    print('Starting cli...')

    # read the schema data from file
    with open(schema, "r") as f:
        # load file into string variable
        file_data = f.read()
        schema_data = cast(list[dict[str, object]], json.loads(file_data))

    target = lang
    output_directory = out

    # Call the generate function
    _generate_internal(schema_data, target, output_directory, package)


# Define the custom filter
def _regex_replace(s: str, find: str, replace: str) -> str:
    """A custom Jinja2 filter to perform regex replacement."""
    return re.sub(find, replace, s)


def _find_schema_key(schema_data: dict[str, object]) -> str:
    for key in schema_data:
        if key.startswith("struct") or key.startswith("union") or key.startswith("fn") or key.startswith("requestHeader") or key.startswith("responseHeader") or key.startswith('info'):
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
        'uapicodegen', 'templates')
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
            if schema_key.startswith('info') or schema_key.startswith('requestHeader') or schema_key.startswith('responseHeader'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            _write_java_file('java_type.j2', {
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
