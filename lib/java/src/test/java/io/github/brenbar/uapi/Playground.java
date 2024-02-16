package io.github.brenbar.uapi;

import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.function.BiFunction;
import java.util.function.Function;

public class Playground {
    public static void main(String[] args) throws IOException {
        // var json = Files.readString(FileSystems.getDefault().getPath("../../test",
        // "example.uapi.json"));
        // var uApi = UApiSchema.fromJson(json);

        // Function<Message, Message> handler = (requestMessage) -> {
        // return new Message(Map.of(), Map.of("Ok", Map.of()));
        // };

        // var server = new Server(uApi, handler, new Server.Options());

        // BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
        // return CompletableFuture.supplyAsync(() -> {
        // var requestBytes = s.serialize(m);
        // var responseBytes = server.process(requestBytes);
        // return s.deserialize(responseBytes);
        // });
        // };

        // var clientOptions = new Client.Options();
        // clientOptions.useBinary = true;
        // clientOptions.timeoutMsDefault = 100000000000L;
        // var client = new Client(adapter, clientOptions);
        // var result = client
        // .request(new Message(Map.of(), Map.of("fn.test", Map.of("value!",
        // Map.of("pStrBool!",
        // Map.of("wrap", 0))))));
        // System.out.println(result.body);

        var r = new _RandomGenerator(3, 3);
        for (var i = 0; i < 100; i += 1) {
            r.nextInt();
            System.out.println(r.seed);
        }
    }
}
