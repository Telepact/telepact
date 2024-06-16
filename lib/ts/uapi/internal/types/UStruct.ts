import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { validate_struct } from 'uapi/internal/validation/ValidateStruct';
import { generate_random_struct } from 'uapi/internal/generation/GenerateRandomStruct';

const _STRUCT_NAME: string = 'Object';

export class UStruct implements UType {
    name: string;
    fields: { [key: string]: UFieldDeclaration };
    type_parameter_count: number;

    constructor(name: string, fields: { [key: string]: UFieldDeclaration }, type_parameter_count: number) {
        this.name = name;
        this.fields = fields;
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
        return validate_struct(value, select, fn, type_parameters, generics, this.name, this.fields);
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
        return generate_random_struct(
            blueprint_value,
            use_blueprint_value,
            include_optional_fields,
            randomize_optional_fields,
            type_parameters,
            generics,
            random,
            this.fields,
        );
    }

    get_name(generics: UTypeDeclaration[]): string {
        return _STRUCT_NAME;
    }
}
