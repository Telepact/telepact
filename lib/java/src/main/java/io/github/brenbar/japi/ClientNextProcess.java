package io.github.brenbar.japi;

import java.util.List;

public interface ClientNextProcess {
    List<Object> proceed(List<Object> japiMessage);
}
