import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';

export class UGeneric extends UType {
    private index: number;

    constructor(index: number) {
        super();
        this.index = index;
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
        const type_declaration = generics[this.index];
        return type_declaration.validate(value, select, fn, []);
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
        const generic_type_declaration = generics[this.index];
        return generic_type_declaration.generate_random_value(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            [],
            random_generator,
        );
    }

    get_name(generics: UTypeDeclaration[]): string {
        const type_declaration = generics[this.index];
        return type_declaration.type.get_name(generics);
    }
}
