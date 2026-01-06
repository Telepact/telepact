# Telepact Prettier Plugin

Keep your Telepact API schemas well-formatted (especially the docstrings) using
this prettier plugin.

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

