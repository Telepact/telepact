package uapitest;

import uapi.Message;
import uapi.Client;
import java.util.Map;

public class ClientInterface_ {

    private final Client client;

    public ClientInterface_(Client client) {
        this.client = client;
    }
    public TypedMessage_<example.Output> example(Map<String, Object> headers, example.Input input) {
        var message = this.client.request(new Message(headers, input.pseudoJson));
        return new TypedMessage_<>(message.headers, new example.Output(message.body));
    }
    public TypedMessage_<getBigList.Output> getBigList(Map<String, Object> headers, getBigList.Input input) {
        var message = this.client.request(new Message(headers, input.pseudoJson));
        return new TypedMessage_<>(message.headers, new getBigList.Output(message.body));
    }
    public TypedMessage_<test.Output> test(Map<String, Object> headers, test.Input input) {
        var message = this.client.request(new Message(headers, input.pseudoJson));
        return new TypedMessage_<>(message.headers, new test.Output(message.body));
    }
}