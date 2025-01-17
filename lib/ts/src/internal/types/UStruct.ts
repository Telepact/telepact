import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateStruct } from '../../internal/validation/ValidateStruct';
import { generateRandomStruct } from '../../internal/generation/GenerateRandomStruct';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const structName: string = 'Object';

export class UStruct implements UType {
    name: string;
    fields: { [key: string]: UFieldDeclaration };

    constructor(name: string, fields: { [key: string]: UFieldDeclaration }) {
        this.name = name;
        this.fields = fields;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateStruct(value, this.name, this.fields, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }

    getName(): string {
        return structName;
    }
}
