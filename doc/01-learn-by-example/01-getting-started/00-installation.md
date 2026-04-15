# 00. Installation

Let's get the few tools we need for the whole walkthrough.

## Install the Telepact CLI

```sh
uv tool install --prerelease=allow telepact-cli
```

## Install the Python library

We'll use this later for the client and server examples.

```sh
pip install --pre telepact requests
```

## Check that everything is ready

```sh
telepact --help
python --version
curl --version
```

From here on, we'll assume:

- `telepact` is on our `PATH`
- `python` is available
- `curl` is available
- we are free to create small scratch files in our own working directory

Next: [01. Ping](./01-ping.md)
