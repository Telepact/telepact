package io.github.brenbar.japi;

import java.util.Map;

public class InternalMessage {

    public static Message convertFnMessage(FnMessage message) {
        return new Message(message.header, Map.of(message.target, message.payload));
    }

    public static FnMessage convertMessage(Message message) {
        var target = message.body.keySet().stream().findAny().get();
        var payload = (Map<String, Object>) message.body.values().stream().findAny().get();
        ;
        return new FnMessage(message.header, target, payload);
    }
}
