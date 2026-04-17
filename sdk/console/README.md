# Telepact Console

The Console is a debugging tool that allows you to easily connect to your
running Telepact server, visualize your API with interactive documentation, and
submit live requests to your server.

## Installation

```
npm install -g telepact-console
```

## Usage

```
npx telepact-console -p 8080
```

Then you can access the UI in your browser at http://localhost:8080.

When launched through the npm CLI, the Console proxies absolute live HTTP and
WebSocket URLs through its own localhost server first. This avoids browser CORS
limits while keeping the self-hosted build unchanged for same-domain embeds.

## Docker

The Console is also available as a docker image, which can be installed directly
from [Releases](https://github.com/Telepact/telepact/releases). You can copy the
link for the Console from the release assets.

Example:

```
curl -L -o telepact-docker.tar.gz https://github.com/Telepact/telepact/releases/download/{version}/docker-image-telepact-console-{version}.tar.gz
docker load < telepact-docker.tar.gz
```

Starting the docker container:

```
docker run -p 8080:8080 telepact-console:{version}
```

For a more concrete usage example, see
[self-hosting example](https://github.com/Telepact/telepact/blob/main/test/console-self-hosted/).
