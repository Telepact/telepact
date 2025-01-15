import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { generateRandomAny } from '../../internal/generation/GenerateRandomAny';
import { GenerateContext } from '../../internal/generation/GenerateContext';

const anyName = 'Any';

export class UAny extends UType {
    getTypeParameterCount(): number {
        return 0;
    }

    validate(
        value: any,
        select: { [key: string]: any } | null,
        fn: string | null,
        typeParameters: UTypeDeclaration[],
    ): ValidationFailure[] {
        return [];
    }

    generateRandomValue(ctx: GenerateContext): any {
        return generateRandomAny(ctx);
    }

    getName(): string {
        return anyName;
    }
}
