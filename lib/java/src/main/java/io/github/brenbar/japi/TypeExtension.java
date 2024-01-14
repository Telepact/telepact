package io.github.brenbar.japi;

import java.util.List;

public interface TypeExtension {

    List<ValidationFailure> validate(Object given, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics);

}
