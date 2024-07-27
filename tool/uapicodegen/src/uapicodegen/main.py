import argparse
import json
from typing import cast, Pattern
import jinja2
import click
from pathlib import Path
import re


def validate_package(ctx: click.Context, param: click.Parameter, value: str) -> str:
    lang = ctx.params.get('lang')
    if lang == 'java' and not value:
        raise click.BadParameter(
            '--package is required when --lang is java')
    return value


@click.command()
@click.option('--schema', help='uAPI schema')
@click.option('--lang', help='Language target')
@click.option('--out', help='Output directory')
@click.option('--package', help='Java package', callback=validate_package)
def main(schema: str, lang: str, out: str, package: str) -> None:

    print('Starting cli...')

    # read the schema data from file
    with open(schema, "r") as f:
        # load file into string variable
        file_data = f.read()
        schema_data = cast(list[dict[str, object]], json.loads(file_data))

    target = lang
    output_directory = out

    # Call the generate function
    generate(schema_data, target, output_directory, package)


# Define the custom filter
def regex_replace(s: str, find: str, replace: str) -> str:
    """A custom Jinja2 filter to perform regex replacement."""
    return re.sub(find, replace, s)


def find_schema_key(schema_data: dict[str, object]) -> str:
    for key in schema_data:
        if key.startswith("struct") or key.startswith("union") or key.startswith("fn"):
            return key
    raise Exception("No schema key found")


def find_case_key(case_data: dict[str, object]) -> str:
    for key in case_data:
        if key != '///':
            return key
    raise Exception("No case key found")


def generate(schema_data: list[dict[str, object]], target: str, output_dir: str, java_package: str) -> None:

    # Load jinja template from file
    # Adjust the path to your template directory if necessary
    template_loader = jinja2.PackageLoader(
        'src.uapicodegen', 'templates')
    template_env = jinja2.Environment(
        loader=template_loader, extensions=['jinja2.ext.do'])

    template_env.filters['regex_replace'] = regex_replace
    template_env.filters['find_schema_key'] = find_schema_key
    template_env.filters['find_case_key'] = find_case_key

    if "java" == target:

        functions = []

        for schema_entry in schema_data:
            schema_key = find_schema_key(schema_entry)

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
            print(server_output)


if __name__ == '__main__':
    main()
