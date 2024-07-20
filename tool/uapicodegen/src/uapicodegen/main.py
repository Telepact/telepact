import argparse
import json
from typing import cast
import jinja2
import click
from pathlib import Path


@click.command()
@click.option('--schema', help='uAPI schema')
@click.option('--lang', help='Language target')
@click.option('--out', help='Output directory')
def main(schema: str, lang: str, out: str) -> None:

    # read the schema data from file
    with open(schema, "r") as f:
        # load file into string variable
        file_data = f.read()
        schema_data = cast(list[dict[str, object]], json.loads(file_data))

    target = lang
    output_directory = out

    # Call the generate function
    generate(schema_data, target, output_directory)


def convert_to_java_type(data_type: str) -> str:
    return {
        "boolean": "boolean",
        "boolean?": "Boolean",
        "integer": "int",
        "integer?": "Integer",
        "string": "String",
        "string?": "String",
        "array": "List",
        "array?": "List",
        "object": "Map",
        "object?": "Map",
        "any": "Object",
        "any?": "Object"
    }[data_type]


def generate(schmea_data: list[dict[str, object]], target: str, output_dir: str) -> None:

    if "java" == target:

        for schema_entry in schmea_data:
            # get first key in dict
            name = list(schema_entry.keys())[0]

            if name.startswith("struct."):

                # Load jinja template from file
                # Adjust the path to your template directory if necessary
                template_loader = jinja2.PackageLoader(
                    'src.uapicodegen', 'templates')
                template_env = jinja2.Environment(loader=template_loader)
                template = template_env.get_template(
                    'java_struct.j2')  # Specify your template file name

                template_env.filters['to_java'] = convert_to_java_type

                # Render the template with context
                output = template.render(schema_entry)

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
