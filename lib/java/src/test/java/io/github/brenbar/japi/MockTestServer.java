package io.github.brenbar.japi;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.ServerSocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;

public class MockTestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketPath = "./frontdoor.socket";

        var path = args[0];
        var json = Files.readString(FileSystems.getDefault().getPath(path));
        var jApi = new JApiSchema(json);

        var server = new MockServer(jApi, new MockServer.Options().setOnError((e) -> e.printStackTrace()));

        var socket = UnixDomainSocketAddress.of(socketPath);
        Files.deleteIfExists(socket.getPath());
        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socket);
            while (true) {
                try (var clientChannel = serverChannel.accept()) {
                    var requestBytes = TestUtility.readSocket(clientChannel);

                    System.out.println("|<--  %s".formatted(new String(requestBytes)));
                    var responseBytes = server.process(requestBytes);
                    System.out.println("|-->  %s".formatted(new String(responseBytes)));

                    var framedResponseBuf = ByteBuffer.allocate(responseBytes.length + 4);
                    framedResponseBuf.putInt(responseBytes.length);
                    framedResponseBuf.put(responseBytes);
                    framedResponseBuf.flip();

                    clientChannel.write(framedResponseBuf);
                }
            }
        }
    }
}
