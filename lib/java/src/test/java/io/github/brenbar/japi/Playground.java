package io.github.brenbar.japi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.function.Function;

import io.github.brenbar.japi.Client.Adapter;

public class Playground {
    public static void main(String[] args) throws IOException {
        var json = Files.readString(FileSystems.getDefault().getPath("../../test", "example.japi.json"));
        var jApi = UApiSchema.fromJson(json);

        Function<Message, Message> handler = (requestMessage) -> {
            return new Message(Map.of("Ok", Map.of()));
        };

        var server = new Server(jApi, handler, new Server.Options());

        Adapter adapter = (m, s) -> {
            return CompletableFuture.supplyAsync(() -> {
                var requestBytes = s.serialize(m);
                var responseBytes = server.process(requestBytes);
                return s.deserialize(responseBytes);
            });
        };

        var clientOptions = new Client.Options();
        clientOptions.useBinaryDefault = true;
        clientOptions.timeoutMsDefault = 100000000000L;
        var client = new Client(adapter, clientOptions);
        var result = client
                .send(new Message(Map.of("fn.test", Map.of("value!", Map.of("pStrBool!", Map.of("wrap", 0))))));
        System.out.println(result.body);
    }
}
