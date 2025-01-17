import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { GenerateContext } from '../../internal/generation/GenerateContext';
import { ValidateContext } from '../validation/ValidateContext';
import { UTypeDeclaration } from './UTypeDeclaration';

export abstract class UType {
    abstract getTypeParameterCount(): number;

    abstract validate(value: any, typeParameters: UTypeDeclaration[], ctx: ValidateContext): ValidationFailure[];

    abstract generateRandomValue(ctx: GenerateContext): any;

    abstract getName(): string;
}
