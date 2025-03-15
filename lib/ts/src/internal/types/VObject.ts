import { VTypeDeclaration } from './VTypeDeclaration';
import { ValidationFailure } from '../validation/ValidationFailure';
import { VType } from './VType';
import { validateObject } from '../validation/ValidateObject';
import { generateRandomObject } from '../generation/GenerateRandomObject';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const objectName: string = 'Object';

export class VObject implements VType {
    getTypeParameterCount(): number {
        return 1;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateObject(value, typeParameters, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomObject(blueprintValue, useBlueprintValue, typeParameters, ctx);
    }

    getName(): string {
        return objectName;
    }
}
