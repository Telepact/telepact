import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UUnion } from '../../internal/types/UUnion';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { generateRandomUnion } from '../../internal/generation/GenerateRandomUnion';
import { ValidateContext } from '../validation/ValidateContext';

const FN_NAME = 'Object';

export class UFn extends UType {
    name: string;
    call: UUnion;
    result: UUnion;
    errorsRegex: string;
    inheritedErrors: string[] = [];

    constructor(name: string, call: UUnion, output: UUnion, errorsRegex: string) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return this.call.validate(value, [], ctx);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomUnion(this.call.cases, ctx);
    }

    getName(): string {
        return FN_NAME;
    }
}
