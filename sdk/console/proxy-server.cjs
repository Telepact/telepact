const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { spawn } = require('child_process');

const app = express();
const target = 'http://localhost:4173'; // Your SvelteKit dev server
const simulationPath = '/s/my-dev-simulation'; // The path you want to test

// Start the target server using npm run preview
const targetServer = spawn('npm', ['run', 'preview'], { stdio: 'inherit' });

targetServer.on('error', (err) => {
    console.error('Failed to start the target server:', err);
    process.exit(1);
});

targetServer.on('exit', (code) => {
    console.log(`Target server exited with code ${code}`);
    process.exit(code);
});

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

// Ensure the target server is terminated when the proxy server exits
process.on('SIGINT', () => {
    targetServer.kill();
    process.exit();
});
process.on('SIGTERM', () => {
    targetServer.kill();
    process.exit();
});