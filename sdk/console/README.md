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
WebSocket URLs through its own localhost server first while keeping the
self-hosted build unchanged for same-domain embeds.

## Self-Hosting Through npm

The same `telepact-console` npm package supports both:

- the CLI entrypoint through `bin`
- the packaged self-hosted static assets through the
  `telepact-console/self-hosted` export

If you are building your own container, install `telepact-console` in a build
stage and copy the packaged assets into your final image. The Console project
no longer publishes a separate Docker image artifact.

Example:

```dockerfile
FROM node:22-alpine AS console
WORKDIR /work

RUN npm init -y
RUN npm install --ignore-scripts --omit=dev telepact-console@{version}
RUN TELEPACT_CONSOLE_ROOT="$(node --input-type=module -e 'import { selfHostedRoot } from "telepact-console/self-hosted"; process.stdout.write(selfHostedRoot)')" \
 && mkdir -p /out \
 && cp -R "$TELEPACT_CONSOLE_ROOT"/. /out/

FROM nginx:alpine
COPY --from=console /out/ /usr/share/nginx/html/
COPY override.js /usr/share/nginx/html/override.js
```

The `telepact-console/self-hosted` export gives you a stable way to resolve the
packaged static asset directory from Node.js. The actual files still come from
the same published `telepact-console` package in `node_modules`.

For a more concrete usage example, see
[self-hosting example](https://github.com/Telepact/telepact/blob/main/test/console-self-hosted/).
