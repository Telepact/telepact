import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { validate_union } from 'uapi/internal/validation/ValidateUnion';
import { generate_random_union } from 'uapi/internal/generation/GenerateRandomUnion';

export const _UNION_NAME: string = 'Object';

export class UUnion implements UType {
    name: string;
    cases: { [key: string]: UStruct };
    case_indices: { [key: string]: number };
    type_parameter_count: number;

    constructor(
        name: string,
        cases: { [key: string]: UStruct },
        case_indices: { [key: string]: number },
        type_parameter_count: number,
    ) {
        this.name = name;
        this.cases = cases;
        this.case_indices = case_indices;
        this.type_parameter_count = type_parameter_count;
    }

    get_type_parameter_count(): number {
        return this.type_parameter_count;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_union(value, select, fn, type_parameters, generics, this.name, this.cases);
    }

    generate_random_value(
        blueprint_value: any,
        use_blueprint_value: boolean,
        include_optional_fields: boolean,
        randomize_optional_fields: boolean,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        random: RandomGenerator,
    ): any {
        return generate_random_union(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            type_parameters,
            generics,
            random,
            this.cases,
        );
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _UNION_NAME;
    }
}
