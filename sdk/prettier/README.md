# Telepact Prettier Plugin

Formats `.telepact.yaml` and `.telepact.yml` schema files to match the checked-in
Telepact schema style:

- `///` docstrings are emitted as YAML `|` block scalars
- Telepact field values stay in inline JSON form

## Installation

```sh
npm install prettier-plugin-telepact
```

## Usage

Add the plugin to your Prettier config:

```json
{
    "plugins": ["prettier-plugin-telepact"]
}
```
