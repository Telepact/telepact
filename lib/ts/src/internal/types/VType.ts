import { ValidationFailure } from '../validation/ValidationFailure';
import { GenerateContext } from '../generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';
import { VTypeDeclaration } from './VTypeDeclaration';

export abstract class VType {
    abstract getTypeParameterCount(): number;

    abstract validate(value: any, typeParameters: VTypeDeclaration[], ctx: ValidateContext): ValidationFailure[];

    abstract generateRandomValue(
        blueprintValue: any,
        useBlueprintValue: boolean,
        typeParameters: VTypeDeclaration[],
        ctx: GenerateContext,
    ): any;

    abstract getName(): string;
}
