package uapi.internal.types;

import static uapi.internal.generation.GenerateRandomValueOfType.generateRandomValueOfType;
import static uapi.internal.validation.ValidateValueOfType.validateValueOfType;

import java.util.List;
import java.util.Map;

import uapi.internal.generation.GenerateContext;
import uapi.internal.validation.ValidationFailure;

public class UTypeDeclaration {
    public final UType type;
    public final boolean nullable;
    public final List<UTypeDeclaration> typeParameters;

    public UTypeDeclaration(
            UType type,
            boolean nullable, List<UTypeDeclaration> typeParameters) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    public List<ValidationFailure> validate(Object value, Map<String, Object> select, String fn) {
        return validateValueOfType(value, select, fn, this.type, this.nullable, this.typeParameters);
    }

    public Object generateRandomValue(GenerateContext ctx) {
        return generateRandomValueOfType(this.type, this.nullable, this.typeParameters, ctx);
    }
}
