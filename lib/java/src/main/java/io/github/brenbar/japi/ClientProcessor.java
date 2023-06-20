package io.github.brenbar.japi;

import java.util.List;

public interface ClientProcessor {
    List<Object> process(List<Object> japiMessage, ClientNextProcess next);

}
