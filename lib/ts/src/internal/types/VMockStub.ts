import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateMockStub } from '../validation/ValidateMockStub';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomUMockStub } from '../generation/GenerateRandomUMockStub';
import { ValidateContext } from '../validation/ValidateContext';

export const mockStubName: string = '_ext.Stub_';

export class VMockStub extends VType {
    types: { [key: string]: VType };

    constructor(types: { [key: string]: VType }) {
        super();
        this.types = types;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(givenObj: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockStub(givenObj, this.types, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUMockStub(this.types, ctx);
    }

    getName(): string {
        return mockStubName;
    }
}
