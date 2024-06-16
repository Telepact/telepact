import { RandomGenerator } from 'uapi/RandomGenerator';
import { UType } from 'uapi/internal/types/UType';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { validate_value_of_type } from 'uapi/internal/validation/ValidateValueOfType';
import { generate_random_value_of_type } from 'uapi/internal/generation/GenerateRandomValueOfType';

export class UTypeDeclaration {
    type: UType;
    nullable: boolean;
    type_parameters: UTypeDeclaration[];

    constructor(type: UType, nullable: boolean, type_parameters: UTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.type_parameters = type_parameters;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_value_of_type(value, select, fn, generics, this.type, this.nullable, this.type_parameters);
    }

    generate_random_value(
        blueprint_value: any,
        use_blueprint_value: boolean,
        include_optional_fields: boolean,
        randomize_optional_fields: boolean,
        generics: UTypeDeclaration[],
        random_generator: RandomGenerator,
    ): any {
        return generate_random_value_of_type(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            generics,
            random_generator,
            this.type,
            this.nullable,
            this.type_parameters,
        );
    }
}
