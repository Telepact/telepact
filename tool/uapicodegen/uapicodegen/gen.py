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


def _find_case_key(case_data: dict[str, object]) -> str:
    for key in case_data:
        if key != '///':
            return key
    raise Exception("No case key found")


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
    template_env.filters['find_case_key'] = _find_case_key
    template_env.filters['raise_error'] = _raise_error

    if "java" == target:

        functions = []

        for schema_entry in schema_data:
            schema_key = _find_schema_key(schema_entry)
            if schema_key.startswith('info') or schema_key.startswith('requestHeader') or schema_key.startswith('responseHeader'):
                continue

            if schema_key.startswith("fn"):
                functions.append(schema_key)

            type_template = template_env.get_template(
                'java_type.j2')  # Specify your template file name

            translated_entry = {
                'package': java_package,
                'data': schema_entry
            }

            output = type_template.render(translated_entry)

            # Write the output to a file
            if output_dir:
                # Create the Path object for the directory
                output_path = Path(output_dir)

                # Ensure the directory exists
                output_path.mkdir(parents=True, exist_ok=True)

                # Use the / operator provided by pathlib to concatenate paths
                file_name = schema_key.split('.')[1]

                file_path = output_path / f"{file_name}.java"

                # Open the file for writing
                with file_path.open("w") as f:
                    f.write(output)

            else:
                print(output)

        server_template = template_env.get_template(
            'java_server.j2')

        server_output = server_template.render(
            {'package': java_package, 'functions': functions})

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            # Use the / operator provided by pathlib to concatenate paths
            file_name = schema_key.split('.')[1]

            file_path = output_path / f"ServerHandler_.java"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(server_output)

        else:
            print(server_output)

        client_template = template_env.get_template(
            'java_client.j2')

        client_output = client_template.render(
            {'package': java_package, 'functions': functions})

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            # Use the / operator provided by pathlib to concatenate paths
            file_name = schema_key.split('.')[1]

            file_path = output_path / f"ClientInterface_.java"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(client_output)

        else:
            print(client_output)

        opt_template = template_env.get_template(
            'java_optional.j2')

        opt_output = opt_template.render(
            {'package': java_package})

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            # Use the / operator provided by pathlib to concatenate paths
            file_name = schema_key.split('.')[1]

            file_path = output_path / f"Optional_.java"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(opt_output)

        else:
            print(opt_output)

        util_template = template_env.get_template(
            'java_utility.j2')

        util_output = util_template.render(
            {'package': java_package})

        # Write the output to a file
        if output_dir:
            # Create the Path object for the directory
            output_path = Path(output_dir)

            # Ensure the directory exists
            output_path.mkdir(parents=True, exist_ok=True)

            # Use the / operator provided by pathlib to concatenate paths
            file_name = schema_key.split('.')[1]

            file_path = output_path / f"Utility_.java"

            # Open the file for writing
            with file_path.open("w") as f:
                f.write(util_output)

        else:
            print(util_output)
