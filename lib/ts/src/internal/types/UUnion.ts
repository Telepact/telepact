import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { validateUnion } from '../../internal/validation/ValidateUnion';
import { generateRandomUnion } from '../../internal/generation/GenerateRandomUnion';
import { UType } from '../../internal/types/UType';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const unionName: string = 'Object';

export class UUnion implements UType {
    name: string;
    cases: { [key: string]: UStruct };
    caseIndices: { [key: string]: number };

    constructor(name: string, cases: { [key: string]: UStruct }, caseIndices: { [key: string]: number }) {
        this.name = name;
        this.cases = cases;
        this.caseIndices = caseIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateUnion(value, this.name, this.cases, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(this.cases, ctx);
    }

    getName(): string {
        return unionName;
    }
}
