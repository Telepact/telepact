import { RandomGenerator } from '../../RandomGenerator';
import { VTypeDeclaration } from '../types/VTypeDeclaration';

export class GenerateContext {
    includeOptionalFields: boolean;
    randomizeOptionalFields: boolean;
    alwaysIncludeRequiredFields: boolean;
    fnScope: string;
    randomGenerator: RandomGenerator;

    constructor(
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        alwaysIncludeRequiredFields: boolean,
        fnScope: string,
        randomGenerator: RandomGenerator,
    ) {
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.alwaysIncludeRequiredFields = alwaysIncludeRequiredFields;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }

    copy({
        alwaysIncludeRequiredFields,
    }: {
        blueprintValue?: any;
        useBlueprintValue?: boolean;
        typeParameters?: VTypeDeclaration[];
        alwaysIncludeRequiredFields?: boolean;
    }): GenerateContext {
        return new GenerateContext(
            this.includeOptionalFields,
            this.randomizeOptionalFields,
            alwaysIncludeRequiredFields ?? this.alwaysIncludeRequiredFields,
            this.fnScope,
            this.randomGenerator,
        );
    }
}
