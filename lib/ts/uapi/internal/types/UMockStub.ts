import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validate_mock_stub } from 'uapi/internal/validation/ValidateMockStub';

const _MOCK_STUB_NAME: string = '_ext.Stub_';

export class UMockStub extends UType {
    types: { [key: string]: UType };

    constructor(types: { [key: string]: UType }) {
        super();
        this.types = types;
    }

    get_type_parameter_count(): number {
        return 0;
    }

    validate(
        given_obj: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        type_parameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validate_mock_stub(given_obj, select, fn, type_parameters, generics, this.types);
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
        return _MOCK_STUB_NAME;
    }
}
