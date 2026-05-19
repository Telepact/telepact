//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

import java.util.HashMap;
import java.util.Map;

/**
 * A telepact Message.
 */
public class Message {
    /**
     * Headers of the message.
     */
    public final Map<String, Object> headers;

    /**
     * Body of the message.
     */
    public final Map<String, Object> body;

    /**
     * Constructs a Message with the specified headers and body.
     *
     * @param header the headers of the message
     * @param body the body of the message
     */
    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.headers = new HashMap<>(header);
        this.body = body;
    }

    /**
     * Retrieves the target from the message body.
     *
     * @return the target as a String
     */
    public String getBodyTarget() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return entry.getKey();
    }

    /**
     * Retrieves the payload from the message body.
     *
     * @return the payload as a Map
     */
    public Map<String, Object> getBodyPayload() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return (Map<String, Object>) entry.getValue();
    }
}
