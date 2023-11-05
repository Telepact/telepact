package io.github.brenbar.japi;

import java.util.List;

public interface TypeExtension {

    List<ValidationFailure> validate(String path, Object given, JApiSchema jApiSchema);

}
