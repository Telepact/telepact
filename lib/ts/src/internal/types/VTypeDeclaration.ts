import { VType } from './VType';
import { ValidationFailure } from '../validation/ValidationFailure';
import { validateValueOfType } from '../validation/ValidateValueOfType';
import { generateRandomValueOfType } from '../generation/GenerateRandomValueOfType';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export class VTypeDeclaration {
    type: VType;
    nullable: boolean;
    typeParameters: VTypeDeclaration[];

    constructor(type: VType, nullable: boolean, typeParameters: VTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    validate(value: any, ctx: ValidateContext): ValidationFailure[] {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }

    generateRandomValue(blueprintValue: any, useBlueprintValue: boolean, ctx: GenerateContext): any {
        return generateRandomValueOfType(
            blueprintValue,
            useBlueprintValue,
            this.type,
            this.nullable,
            this.typeParameters,
            ctx,
        );
    }
}
