# Telepact Console

The Console is a debugging tool that allows you to easily connect to your
running Telepact server, visualize your API with interactive documentation, and
submit live requests to your server.

## Installation

```
npm install --ignore-scripts -g telepact-console
```

## Usage

```
npx telepact-console -p 8080
```

Then you can access the UI in your browser at http://localhost:8080.

## Docker

The Console is also available as a docker image, which can be installed directly from
[Releases](https://github.com/Telepact/telepact/releases). You can copy the link
for the Console from the release assets.

Example:

```
curl -L -o telepact-docker.tar.gz https://github.com/Telepact/telepact/releases/download/1.0.0-alpha.102/docker-image-telepact-console-1.0.0-alpha.102.tar.gz
docker load < telepact-docker.tar.gz
```

Starting the docker container:

```
docker run -p 8080:8080 telepact-console:1.0.0-alpha.102
```

For a more concrete usage example, see
[self-hosting example](https://github.com/Telepact/telepact/blob/main/test/console-self-hosted/).
