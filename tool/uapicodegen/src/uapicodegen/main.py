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


def generate(schema_data: list[dict[str, object]], target: str, output_dir: str, java_package: str) -> None:

    if "java" == target:

        for schema_entry in schema_data:
            # get first key in dict
            schema_name = list(schema_entry.keys())[0]

            if schema_name.startswith("struct"):

                name = schema_name.split(".")[1]

                fields = cast(dict[str, object], schema_entry[schema_name])

                # Load jinja template from file
                # Adjust the path to your template directory if necessary
                template_loader = jinja2.PackageLoader(
                    'src.uapicodegen', 'templates')
                template_env = jinja2.Environment(
                    loader=template_loader, extensions=['jinja2.ext.do'])

                template_env.filters['regex_replace'] = regex_replace

                template = template_env.get_template(
                    'java_struct.j2')  # Specify your template file name

                translated_entry = {
                    'package': java_package,
                    'name': schema_name,
                    'fields': [{'name': k, 'type': v} for k, v in fields.items()],
                }

                # Render the template with context
                print(f'Using schema entry: {translated_entry}')

                output = template.render(translated_entry)

                print(output)

                # Write the output to a file
                if output_dir:
                    # Create the Path object for the directory
                    output_path = Path(output_dir)

                    # Ensure the directory exists
                    output_path.mkdir(parents=True, exist_ok=True)

                    # Use the / operator provided by pathlib to concatenate paths
                    file_path = output_path / f"{name}.java"

                    # Open the file for writing
                    with file_path.open("w") as f:
                        f.write(output)

                else:
                    print(output)


if __name__ == '__main__':
    main()
