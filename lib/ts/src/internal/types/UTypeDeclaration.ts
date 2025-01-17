import { UType } from '../../internal/types/UType';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateValueOfType } from '../../internal/validation/ValidateValueOfType';
import { generateRandomValueOfType } from '../../internal/generation/GenerateRandomValueOfType';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export class UTypeDeclaration {
    type: UType;
    nullable: boolean;
    typeParameters: UTypeDeclaration[];

    constructor(type: UType, nullable: boolean, typeParameters: UTypeDeclaration[]) {
        this.type = type;
        this.nullable = nullable;
        this.typeParameters = typeParameters;
    }

    validate(value: any, ctx: ValidateContext): ValidationFailure[] {
        return validateValueOfType(value, this.type, this.nullable, this.typeParameters, ctx);
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomValueOfType(this.type, this.nullable, this.typeParameters, ctx);
    }
}
