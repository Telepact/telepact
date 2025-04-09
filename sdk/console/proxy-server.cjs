const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const target = 'http://localhost:4173'; // Your SvelteKit dev server
const simulationPath = '/s/my-dev-simulation'; // The path you want to test

app.use(simulationPath, createProxyMiddleware({
    target: target,
    changeOrigin: true,
    pathRewrite: {
        [`^${simulationPath}`]: '', // Remove the prefix when forwarding
    },
    ws: true, // Important for HMR (WebSocket proxying)
}));

// Optional: Add a simple root handler for clarity
app.get('/', (req, res) => {
  res.send(`Proxy active. Access your app at <a href="http://localhost:${proxyPort}${simulationPath}">${simulationPath}</a>`);
});


const proxyPort = 8080; // Choose a port for the proxy
app.listen(proxyPort, () => {
    console.log(`Reverse proxy listening on http://localhost:${proxyPort}`);
    console.log(`Forwarding ${simulationPath}/* to ${target}/`);
});