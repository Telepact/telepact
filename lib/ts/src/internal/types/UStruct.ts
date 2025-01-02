import { RandomGenerator } from '../../RandomGenerator';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UType } from '../../internal/types/UType';
import { validateStruct } from '../../internal/validation/ValidateStruct';
import { generateRandomStruct } from '../../internal/generation/GenerateRandomStruct';

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

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateStruct(value, select, fn, this.name, this.fields);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        random: RandomGenerator,
    ): any {
        return generateRandomStruct(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            random,
            this.fields,
        );
    }

    getName(): string {
        return structName;
    }
}
