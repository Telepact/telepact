package io.github.brenbar.japi;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;

public class TestServer {

    private static byte[] readSocket(SocketChannel socket) throws IOException {
        var lengthBuf = ByteBuffer.allocate(4);
        socket.read(lengthBuf);
        System.out.println("|length buffer %s".formatted(HexFormat.of().formatHex(lengthBuf.array())));
        lengthBuf.flip();
        var length = lengthBuf.getInt();
        System.out.println("|length %d".formatted(length));

        var length_received = 0;

        var finalBuf = ByteBuffer.allocate(8192);

        while (length_received < length) {
            var buf = ByteBuffer.allocate(4096);
            var byteCount = socket.read(buf);
            length_received += byteCount;
            finalBuf.put(buf.flip());
        }

        finalBuf.flip();

        var array = finalBuf.array();

        System.out.println("|buf %s".formatted(new String(array)));

        return array;
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        var fifoPath = "./frontdoor.fifo";
        var fifoBackdoorPath = "./backdoor.fifo";
        var fifoRetPath = "./frontdoor_ret.fifo";
        var fifoRetBackdoorPath = "./backdoor_ret.fifo";
        var socketPath = "./frontdoor.socket";
        var socketBackdoorPath = "./backdoor.socket";

        var path = args[0];
        var json = Files.readString(FileSystems.getDefault().getPath(path));
        var jApi = new JApiSchema(json);
        var objectMapper = new ObjectMapper();

        var backdoorSocket = UnixDomainSocketAddress.of(socketBackdoorPath);

        Function<Message, Message> handler = (requestMessage) -> {
            try (var backdoorChannel = SocketChannel.open(backdoorSocket)) {
                var requestHeaders = requestMessage.header;
                var requestBody = requestMessage.body;
                var requestPseudoJson = List.of(requestHeaders, requestBody);
                var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                System.out.println("|>    %s".formatted(new String(requestBytes)));

                // var requestBuf = ByteBuffer.wrap(requestBytes);
                var framedRequestBuf = ByteBuffer.allocate(requestBytes.length + 4);
                framedRequestBuf.putInt(requestBytes.length);
                framedRequestBuf.put(requestBytes);
                framedRequestBuf.flip();

                backdoorChannel.write(framedRequestBuf);

                // Files.write(Path.of(fifoRetBackdoorPath), requestBytes);

                // var in = new BufferedReader(new InputStreamReader(new
                // FileInputStream(fifoBackdoorPath)));
                // var buf = ByteBuffer.allocate(2048);
                // int b = 0;
                // while ((b = in.read()) >= 0) {
                // buf.put((byte) b);
                // }
                // var responseBytes = buf.array();

                var responseBytes = readSocket(backdoorChannel);

                System.out.println("|<    %s".formatted(new String(responseBytes)));

                var responsePseudoJson = objectMapper.readValue(responseBytes, List.class);
                var responseHeaders = (Map<String, Object>) responsePseudoJson.get(0);
                var responseBody = (Map<String, Object>) responsePseudoJson.get(1);
                return new Message(responseHeaders, responseBody);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

        // while (true) {

        // var in = new BufferedReader(new InputStreamReader(new
        // FileInputStream(fifoPath)));
        // var buf = ByteBuffer.allocate(1024);
        // int b = 0;
        // while ((b = in.read()) >= 0) {
        // buf.put((byte) b);
        // }
        // var requestBytes = buf.array();

        // System.out.println("|<-- %s".formatted(new String(requestBytes)));
        // var responseBytes = server.process(requestBytes);
        // System.out.println("|--> %s".formatted(new String(responseBytes)));

        // Files.write(Path.of(fifoRetPath), responseBytes);
        // }

        var socket = UnixDomainSocketAddress.of(socketPath);
        Files.deleteIfExists(socket.getPath());
        try (var serverChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)) {
            serverChannel.bind(socket);
            while (true) {
                try (var clientChannel = serverChannel.accept()) {
                    var requestBytes = readSocket(clientChannel);

                    System.out.println("|<--  %s".formatted(new String(requestBytes)));
                    var responseBytes = server.process(requestBytes);
                    System.out.println("|-->  %s".formatted(new String(responseBytes)));

                    // var responseBuf = ByteBuffer.wrap(responseBytes);
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
