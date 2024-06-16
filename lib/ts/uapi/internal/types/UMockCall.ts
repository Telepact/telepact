import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validate_mock_call } from 'uapi/internal/validation/ValidateMockCall';

export class UMockCall extends UType {
    private static _MOCK_CALL_NAME: string = '_ext.Call_';
    private types: { [key: string]: UType };

    constructor(types: { [key: string]: UType }) {
        super();
        this.types = types;
    }

    public get_type_parameter_count(): number {
        return 0;
    }

    public validate(
        given_obj: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_mock_call(given_obj, select, fn, type_parameters, generics, this.types);
    }

    public generate_random_value(
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

    public get_name(generics: UTypeDeclaration[]): string {
        return UMockCall._MOCK_CALL_NAME;
    }
}
