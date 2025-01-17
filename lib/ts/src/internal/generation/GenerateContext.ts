import { RandomGenerator } from '../../RandomGenerator';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';

export class GenerateContext {
    blueprintValue: any;
    useBlueprintValue: boolean;
    includeOptionalFields: boolean;
    randomizeOptionalFields: boolean;
    alwaysIncludeRequiredFields: boolean;
    typeParameters: UTypeDeclaration[];
    fnScope: string;
    randomGenerator: RandomGenerator;

    constructor(
        blueprintValue: any,
        useBlueprintValue: boolean,
        includeOptionalFields: boolean,
        randomizeOptionalFields: boolean,
        alwaysIncludeRequiredFields: boolean,
        typeParameters: UTypeDeclaration[],
        fnScope: string,
        randomGenerator: RandomGenerator,
    ) {
        this.blueprintValue = blueprintValue;
        this.useBlueprintValue = useBlueprintValue;
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.typeParameters = typeParameters;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }

    copy({
        blueprintValue,
        useBlueprintValue,
        typeParameters,
        alwaysIncludeRequiredFields,
    }: {
        blueprintValue?: any;
        useBlueprintValue?: boolean;
        typeParameters?: UTypeDeclaration[];
        alwaysIncludeRequiredFields?: boolean;
    }): GenerateContext {
        return new GenerateContext(
            blueprintValue ?? this.blueprintValue,
            useBlueprintValue ?? this.useBlueprintValue,
            this.includeOptionalFields,
            this.randomizeOptionalFields,
            alwaysIncludeRequiredFields ?? this.alwaysIncludeRequiredFields,
            typeParameters ?? this.typeParameters,
            this.fnScope,
            this.randomGenerator,
        );
    }
}
