import io.github.telepact.Client;
import io.github.telepact.Message;
import io.github.telepact.Serializer;

BiFunction<Message, Serializer, Future<Message>> adapter = (message, serializer) ->
    CompletableFuture.supplyAsync(() -> {
        var requestBytes = serializer.serialize(message);
        var responseBytes = transport.send(requestBytes);
        return serializer.deserialize(responseBytes);
    });

var client = new Client(adapter, new Client.Options());
var request = new Message(
    Map.of(),
    Map.of("fn.divide", Map.of("x", 10, "y", 2))
);
var response = client.request(request);

if ("Ok_".equals(response.getBodyTarget())) {
    System.out.println(response.getBodyPayload().get("result"));
}
