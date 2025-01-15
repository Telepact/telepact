import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { GenerateContext } from '../../internal/generation/GenerateContext';

export abstract class UType {
    abstract getTypeParameterCount(): number;

    abstract validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[];

    abstract generateRandomValue(ctx: GenerateContext): any;

    abstract getName(): string;
}
