# Telepact Prettier Plugin

Keep your Telepact API schemas well-formatted (especially the docstrings) using
this prettier plugin.

For most checked-in schema authoring, prefer `*.telepact.yaml`, since YAML block
scalars make multi-line docstrings much cleaner. This plugin is mainly for
teams that still author `*.telepact.json` directly.

## Installation
```
npm install prettier-plugin-telepact
```

## Usage

This plugin requires prettier configuration, for example, in the `.prettierrc` file:
```json
{
    "plugins": ["prettier-plugin-telepact"],
    "overrides": [
        {
            "files": "*.telepact.json",
            "options": {
                "parser": "telepact-parse"
            }
        }
    ]
}
```

For a real-use example, see
[example prettier config file](https://github.com/Telepact/telepact/blob/main/.prettierrc).

