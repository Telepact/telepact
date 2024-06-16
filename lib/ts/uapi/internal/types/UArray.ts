import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { validate_array } from 'uapi/internal/validation/ValidateArray';
import { generate_random_array } from 'uapi/internal/generation/GenerateRandomArray';

const _ARRAY_NAME = 'Array';

export class UArray extends UType {
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
        return validate_array(value, select, fn, type_parameters, generics);
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
        return generate_random_array(
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
        return _ARRAY_NAME;
    }
}
