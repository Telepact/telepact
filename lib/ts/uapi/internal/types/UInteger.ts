import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { validate_integer } from 'uapi/internal/validation/ValidateInteger';
import { generate_random_integer } from 'uapi/internal/generation/GenerateRandomInteger';

const _INTEGER_NAME: string = 'Integer';

export class UInteger extends UType {
    get_type_parameter_count(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_integer(value);
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
        return generate_random_integer(blueprint_value, use_blueprint_value, random_generator);
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _INTEGER_NAME;
    }
}
