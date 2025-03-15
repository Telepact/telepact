import { VTypeDeclaration } from './VTypeDeclaration';
import { VUnion } from './VUnion';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { GenerateContext } from '../generation/GenerateContext';
import { generateRandomUnion } from '../generation/GenerateRandomUnion';
import { ValidateContext } from '../validation/ValidateContext';

const FN_NAME = 'Object';

export class VFn extends VType {
    name: string;
    call: VUnion;
    result: VUnion;
    errorsRegex: string;
    inheritedErrors: string[] = [];

    constructor(name: string, call: VUnion, output: VUnion, errorsRegex: string) {
        super();
        this.name = name;
        this.call = call;
        this.result = output;
        this.errorsRegex = errorsRegex;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return this.call.validate(value, [], ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.call.tags, ctx);
    }

    getName(): string {
        return FN_NAME;
    }
}
