import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateMockStub } from '../../internal/validation/ValidateMockStub';

export const mockStubName: string = '_ext.Stub_';

export class UMockStub extends UType {
    types: { [key: string]: UType };

    constructor(types: { [key: string]: UType }) {
        super();
        this.types = types;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        givenObj: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateMockStub(givenObj, select, fn, typeParameters, generics, this.types);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        throw new Error('Not implemented');
    }

    getName(generics: UTypeDeclaration[]): string {
        return mockStubName;
    }
}
