import { RandomGenerator } from 'uapi/RandomGenerator';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { validateMockCall } from 'uapi/internal/validation/ValidateMockCall';

export const mockCallName: string = '_ext.Call_';

export class UMockCall extends UType {
    private types: { [key: string]: UType };

    constructor(types: { [key: string]: UType }) {
        super();
        this.types = types;
    }

    public getTypeParameterCount(): number {
        return 0;
    }

    public validate(
        givenObj: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
    ): ValidationFailure[] {
        return validateMockCall(givenObj, select, fn, typeParameters, generics, this.types);
    }

    public generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        typeParameters: UTypeDeclaration[],
        generics: UTypeDeclaration[],
        randomGenerator: RandomGenerator,
    ): any {
        throw new Error('Not implemented');
    }

    public getName(generics: UTypeDeclaration[]): string {
        return mockCallName;
    }
}
