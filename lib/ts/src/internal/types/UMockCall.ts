import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateMockCall } from '../../internal/validation/ValidateMockCall';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomUMockCall } from '../../internal/generation/GenerateRandomUMockCall';
import { ValidateContext } from '../validation/ValidateContext';

export const mockCallName: string = '_ext.Call_';

export class UMockCall extends UType {
    private types: { [key: string]: UType };

    constructor(types: { [key: string]: UType }) {
        super();
        this.types = types;
    }

    public getTypeParameterCount(): number {
        return 0;
    }

    public validate(givenObj: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockCall(givenObj, this.types, ctx);
    }

    public generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUMockCall(this.types, ctx);
    }

    public getName(): string {
        return mockCallName;
    }
}
