package io.github.brenbar.japi;

import java.util.List;

public interface TypeExtension {

    String getName();

    List<ValidationFailure> validate(String path, Object given);

}
