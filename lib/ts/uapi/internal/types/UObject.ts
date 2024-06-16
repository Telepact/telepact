import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validate_object } from 'uapi/internal/validation/ValidateObject';
import { generate_random_object } from 'uapi/internal/generation/GenerateRandomObject';

const _OBJECT_NAME: string = 'Object';

export class UObject implements UType {
    get_type_parameter_count(): number {
        return 1;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_object(value, select, fn, type_parameters, generics);
    }

    generate_random_value(
        blueprint_value: any,
        use_blueprint_value: boolean,
        include_optional_fields: boolean,
        randomize_optional_fields: boolean,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        random_generator: RandomGenerator,
    ): any {
        return generate_random_object(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            type_parameters,
            generics,
            random_generator,
        );
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _OBJECT_NAME;
    }
}
