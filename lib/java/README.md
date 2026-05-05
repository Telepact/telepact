## Telepact Library for Java

### Java version

Requires **Java 21**.

### Installation
```xml
<dependency>
    <groupId>io.github.telepact</groupId>
    <artifactId>telepact</artifactId>
</dependency>
```

### Usage

API:
```yaml
- fn.greet:
    subject: string
  ->:
    Ok_:
      message: string
```

Server:
```java
import io.github.telepact.Client;
import io.github.telepact.FunctionRoute;
import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Serializer;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;

var files = new TelepactSchemaFiles("./directory/containing/api/files");
var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
// The schema directory may contain multiple *.telepact.yaml and
// *.telepact.json files. Subdirectories are rejected.
Map<String, FunctionRoute> functionRoutes = Map.of(
    "fn.greet",
    (functionName, requestMessage) -> {
        var arguments = (Map<String, Object>) requestMessage.body.get(functionName);
        var subject = (String) arguments.get("subject");
        return new Message(Map.of(), Map.of("Ok_", Map.of("message", "Hello %s!".formatted(subject))));
    }
);
var options = new Server.Options();
// Set this to false when your schema does not define union.Auth_.
options.middleware = (requestMessage, functionRouter) -> {
    var functionName = requestMessage.getBodyTarget();
    try {
        log.info("Function started", Map.of("function", functionName));
        return functionRouter.route(requestMessage);
    } finally {
        log.info("Function finished", Map.of("function", functionName));
    }
};
var functionRouter = new FunctionRouter(functionRoutes);
var server = new Server(schema, functionRouter, options);


// Wire up request/response bytes from your transport of choice
transport.receive((requestBytes) -> {
    var response = server.process(requestBytes);
    return response.bytes;
});
```

Client:
```java
BiFunction<Message, Serializer, Future<Message>> adapter = (m, s) -> {
    return CompletableFuture.supplyAsync(() -> {
        var requestBytes = s.serialize(m);
        
        // Wire up request/response bytes to your transport of choice
        var responseBytes = transport.send(requestBytes);
        
        return s.deserialize(responseBytes);
    });
};
var options = new Client.Options();
var client = new Client(adapter, options);

var request = new Message(
    Map.of(),
    Map.of("fn.greet", Map.of("subject", "World"))
);
var response = client.request(request);
if ("Ok_".equals(response.getBodyTarget())) {
    var okPayload = response.getBodyPayload();
    System.out.println(okPayload.get("message"));
} else {
    throw new RuntimeException("Unexpected response: " + response.body);
}
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/java/src/main/java/telepacttest/Main.java).
