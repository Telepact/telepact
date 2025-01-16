import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateMockStub } from '../../internal/validation/ValidateMockStub';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomUMockStub } from '../../internal/generation/GenerateRandomUMockStub';

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
    ): ValidationFailure[] {
        return validateMockStub(givenObj, select, fn, this.types);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomUMockStub(this.types, ctx);
    }

    getName(): string {
        return mockStubName;
    }
}
