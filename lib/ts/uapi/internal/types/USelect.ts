import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validate_select } from 'uapi/internal/validation/ValidateSelect';

export type USelectTypes = Record<string, UType>;

const _SELECT: string = 'Object';

export class USelect implements UType {
    types: USelectTypes;

    constructor(types: USelectTypes) {
        this.types = types;
    }

    get_type_parameter_count(): number {
        return 0;
    }

    validate(
        given_obj: any,
        select: Record<string, any> | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_select(given_obj, select, fn, type_parameters, generics, this.types);
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
        throw new Error('Not implemented');
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _SELECT;
    }
}
