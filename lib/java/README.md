## Telepact

### Installation
```xml
<dependency>
    <groupId>io.github.telepact</groupId>
    <artifactId>telepact</artifactId>
    <version>1.0.0-alpha.95</version>
</dependency>
```

### Usage

API:
```json
[
    {
        "fn.greet": {
            "subject": "string"
        },
        "->": {
            "Ok_": {
                "message": "string"
            }
        }
    }
]
```

Server:
```java
var files = new TelepactSchemaFiles("./directory/containing/api/files");
var schema = TelepactSchema.fromFilesJsonMap(files.filenamesToJson)
Function<Message, Message> handler = (requestMessage) -> {
    var functionName = requestMessage.body.keySet().stream().findAny();
    var arguments = (Map<String, Object>) requestMessage.body.get(functionName);

    try {
        // Early in the handler, perform any pre-flight "middleware" operations, such as
        // authentication, tracing, or logging.
        log.info("Function started", Map.of("function", functionName));

        // Dispatch request to appropriate function handling code.
        // (This example uses manual dispatching, but you can also use a more advanced pattern.)
        if (functionName.equals("fn.greet")) {
            var subject = (String) arguments.get("subject");
            return new Message(Map.of(), Map.of("Ok_", Map.of("message": "Hello %s!".formatted(subject))));
        }

        throw new RuntimeException("Function not found");
    } finally {
        // At the end the handler, perform any post-flight "middleware" operations
        log.info("Function finished", Map.of("function", functionName));
    }
};
var options = new Server.Options();
var server = new Server(schema, handler, options);


// Wire up request/response bytes from your transport of choice
transport.receive((requestBytes) -> {
    var responseBytes = server.process(requestBytes);
    return responseBytes;
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
```

For more concrete usage examples, [see the tests](https://github.com/Telepact/telepact/blob/main/test/lib/java/src/main/java/telepacttest/Main.java).