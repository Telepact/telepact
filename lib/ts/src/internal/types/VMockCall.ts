import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateMockCall } from '../validation/ValidateMockCall';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomUMockCall } from '../generation/GenerateRandomUMockCall';
import { ValidateContext } from '../validation/ValidateContext';

export const mockCallName: string = '_ext.Call_';

export class VMockCall extends VType {
    private types: { [key: string]: VType };

    constructor(types: { [key: string]: VType }) {
        super();
        this.types = types;
    }

    public getTypeParameterCount(): number {
        return 0;
    }

    public validate(givenObj: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateMockCall(givenObj, this.types, ctx);
    }

    public generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUMockCall(this.types, ctx);
    }

    public getName(): string {
        return mockCallName;
    }
}
