import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateMockStub } from '../../internal/validation/ValidateMockStub';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomUMockStub } from '../../internal/generation/GenerateRandomUMockStub';
import { ValidateContext } from '../validation/ValidateContext';

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

    validate(givenObj: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockStub(givenObj, this.types, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUMockStub(this.types, ctx);
    }

    getName(): string {
        return mockStubName;
    }
}
