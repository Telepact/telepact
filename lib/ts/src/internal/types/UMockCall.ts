import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { validateMockCall } from '../../internal/validation/ValidateMockCall';
import { GenerateContext } from '../../internal/generation/GenerateContext';

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

    public validate(
        givenObj: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateMockCall(givenObj, select, fn, this.types);
    }

    public generateRandomValue(ctx: GenerateContext): any {
        throw new Error('Not implemented');
    }

    public getName(): string {
        return mockCallName;
    }
}
