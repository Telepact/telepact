package uapi.internal.types;

import java.util.List;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidateContext;
import uapi.internal.validation.ValidationFailure;

public interface UType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value,
                        List<UTypeDeclaration> typeParameters, ValidateContext ctx);

        public Object generateRandomValue(GenerateContext ctx);

        public String getName();
}
