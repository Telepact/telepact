package uapitest;

import uapi.Message;
import java.util.Map;

public abstract class ServerHandler_ {
    public abstract TypedMessage_<example.Output> example(Map<String, Object> headers, example.Input input);
    public abstract TypedMessage_<getBigList.Output> getBigList(Map<String, Object> headers, getBigList.Input input);
    public abstract TypedMessage_<test.Output> test(Map<String, Object> headers, test.Input input);

    public Message handler(Message message) {
        var functionName = message.body.keySet().stream().findAny().get();
        switch (functionName) {
            case "fn.example" -> {
                var typedMessage = this.example(message.headers, new example.Input(message.body));
                return new Message(typedMessage.headers, typedMessage.body.pseudoJson);
            }
            case "fn.getBigList" -> {
                var typedMessage = this.getBigList(message.headers, new getBigList.Input(message.body));
                return new Message(typedMessage.headers, typedMessage.body.pseudoJson);
            }
            case "fn.test" -> {
                var typedMessage = this.test(message.headers, new test.Input(message.body));
                return new Message(typedMessage.headers, typedMessage.body.pseudoJson);
            }
            default -> throw new IllegalArgumentException("Unknown function: " + functionName);
        }
    }

}