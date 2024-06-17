import { RandomGenerator } from 'uapi/RandomGenerator';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { validateStruct } from 'uapi/internal/validation/ValidateStruct';
import { generateRandomStruct } from 'uapi/internal/generation/GenerateRandomStruct';

export const structName: string = 'Object';

export class UStruct implements UType {
    name: string;
    fields: { [key: string]: UFieldDeclaration };
    typeParameterCount: number;

    constructor(name: string, fields: { [key: string]: UFieldDeclaration }, typeParameterCount: number) {
        this.name = name;
        this.fields = fields;
        this.typeParameterCount = typeParameterCount;
    }

    getTypeParameterCount(): number {
        return this.typeParameterCount;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateStruct(value, select, fn, typeParameters, generics, this.name, this.fields);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        random: RandomGenerator,
    ): any {
        return generateRandomStruct(
            blueprintValue,
            useBlueprintValue,
            includeOptionalFields,
            randomizeOptionalFields,
            typeParameters,
            generics,
            random,
            this.fields,
        );
    }

    getName(generics: UTypeDeclaration[]): string {
        return structName;
    }
}
