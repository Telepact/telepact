package io.github.brenbar.japi;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.japi.Server.Options;

public class TestServer {

    public static void main(String[] args) throws IOException, InterruptedException {
        var socketPath = "./testServer.socket";

        var path = args[0];
        var json = Files.readString(FileSystems.getDefault().getPath(path));
        var jApi = new JApiSchema(json);
        var objectMapper = new ObjectMapper();

        Function<Message, Message> handler = (requestMessage) -> {
            try {
                var requestHeaders = requestMessage.header;
                var requestBody = requestMessage.body;
                var requestPseudoJson = List.of(requestHeaders, requestBody);
                var requestBytes = objectMapper.writeValueAsBytes(requestPseudoJson);

                Files.write(Path.of(socketPath), requestBytes);

                System.out.println("|> %s".formatted(new String(requestBytes)));

                var in = new FileInputStream(socketPath);
                var buf = ByteBuffer.allocate(1024);
                int b = 0;
                while ((b = in.read()) != -1) {
                    buf.put((byte) b);
                }
                var responseBytes = buf.array();

                System.out.println("|< %s".formatted(new String(responseBytes)));

                var responsePseudoJson = objectMapper.readValue(responseBytes, List.class);
                var responseHeaders = (Map<String, Object>) responsePseudoJson.get(0);
                var responseBody = (Map<String, Object>) responsePseudoJson.get(1);
                return new Message(responseHeaders, responseBody);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };

        var server = new Server(jApi, handler, new Options().setOnError((e) -> e.printStackTrace()));

        while (true) {

            var in = new FileInputStream(socketPath);
            var buf = ByteBuffer.allocate(1024);
            int b = 0;
            while ((b = in.read()) != -1) {
                buf.put((byte) b);
            }
            var requestBytes = buf.array();

            System.out.println("|<-- %s".formatted(new String(requestBytes)));
            var responseBytes = server.process(requestBytes);
            System.out.println("|--> %s".formatted(new String(responseBytes)));

            Files.write(Path.of(socketPath), responseBytes);
        }
    }
}
