import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UUnion } from 'uapi/internal/types/UUnion';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { generate_random_fn } from 'uapi/internal/generation/GenerateRandomFn';

const _FN_NAME = 'Object';

export class UFn extends UType {
    name: string;
    call: UUnion;
    result: UUnion;
    errors_regex: string;

    constructor(name: string, call: UUnion, output: UUnion, errors_regex: string) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errors_regex = errors_regex;
    }

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
        return this.call.validate(value, select, fn, type_parameters, generics);
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
        return generate_random_fn(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            type_parameters,
            generics,
            random_generator,
            this.call.cases,
        );
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _FN_NAME;
    }
}
