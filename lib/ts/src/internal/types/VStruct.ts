import { ValidationFailure } from '../validation/ValidationFailure';
import { VFieldDeclaration } from './VFieldDeclaration';
import { VTypeDeclaration } from './VTypeDeclaration';
import { VType } from './VType';
import { validateStruct } from '../validation/ValidateStruct';
import { generateRandomStruct } from '../generation/GenerateRandomStruct';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const structName: string = 'Object';

export class VStruct implements VType {
    name: string;
    fields: { [key: string]: VFieldDeclaration };

    constructor(name: string, fields: { [key: string]: VFieldDeclaration }) {
        this.name = name;
        this.fields = fields;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateStruct(value, this.name, this.fields, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }

    getName(): string {
        return structName;
    }
}
