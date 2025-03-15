import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { generateRandomAny } from '../generation/GenerateRandomAny';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

const anyName = 'Any';

export class VAny extends VType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return [];
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomAny(ctx);
    }

    getName(): string {
        return anyName;
    }
}
