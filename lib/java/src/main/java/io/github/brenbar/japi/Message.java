package io.github.brenbar.japi;

import java.util.Map;

public interface Message {

    String getTarget();

    Map<String, Object> getHeaders();

    Map<String, Object> getBody();
}
