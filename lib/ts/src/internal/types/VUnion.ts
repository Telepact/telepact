import { ValidationFailure } from '../validation/ValidationFailure';
import { VStruct } from './VStruct';
import { VTypeDeclaration } from './VTypeDeclaration';
import { validateUnion } from '../validation/ValidateUnion';
import { generateRandomUnion } from '../generation/GenerateRandomUnion';
import { VType } from './VType';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';

export const unionName: string = 'Object';

export class VUnion implements VType {
    name: string;
    tags: { [key: string]: VStruct };
    tagIndices: { [key: string]: number };

    constructor(name: string, tags: { [key: string]: VStruct }, tagIndices: { [key: string]: number }) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    getName(): string {
        return unionName;
    }
}
