import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { generate_random_any } from 'uapi/internal/generation/GenerateRandomAny';

const _ANY_NAME = 'Any';

export class UAny extends UType {
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
        return [];
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
        return generate_random_any(random_generator);
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _ANY_NAME;
    }
}
