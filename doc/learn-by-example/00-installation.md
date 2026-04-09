# 00. Installation

Let's get the few things we need for the walkthrough.

## What we will use

- the Telepact CLI
- `curl`
- a terminal with two tabs or windows

## Install the CLI

Telepact publishes the CLI on PyPI.

```sh
uv tool install --prerelease=allow telepact-cli
```

If you do not already have `uv`, install it first from the public `uv`
installation guide: <https://docs.astral.sh/uv/>.

## Sanity check

```sh
telepact --help
```

You should see commands such as `demo-server`, `fetch`, and `mock`.

## One small note before we begin

In the remaining pages, we will assume the CLI is already installed.
Each page starts its own demo or mock server, so we never have to rely on a
previous page still running.

Next: [01. Ping](./01-ping.md)
