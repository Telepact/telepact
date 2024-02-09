import { Server } from 'uapi'

function funTestServer() {
    const server: Server = new Server();
    server.process();
}