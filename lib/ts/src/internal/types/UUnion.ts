import { ValidationFailure } from "../../internal/validation/ValidationFailure";
import { UStruct } from "../../internal/types/UStruct";
import { UTypeDeclaration } from "../../internal/types/UTypeDeclaration";
import { validateUnion } from "../../internal/validation/ValidateUnion";
import { generateRandomUnion } from "../../internal/generation/GenerateRandomUnion";
import { UType } from "../../internal/types/UType";
import { GenerateContext } from "../../internal/generation/GenerateContext";
import { ValidateContext } from "../validation/ValidateContext";

export const unionName: string = "Object";

export class UUnion implements UType {
    name: string;
    tags: { [key: string]: UStruct };
    tagIndices: { [key: string]: number };

    constructor(name: string, tags: { [key: string]: UStruct }, tagIndices: { [key: string]: number }) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    getTypeParameterCount(): number {
        return 0;
    }

    validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[] {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: UTypeDeclaration[],
        ctx: GenerateContext,
    ): any {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    getName(): string {
        return unionName;
    }
}
