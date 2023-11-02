package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;

public interface TypeExtension {

    String getName();

    List<ValidationFailure> validate(String path, Map<String, Object> given);

}
