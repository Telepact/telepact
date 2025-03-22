//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { RandomGenerator } from '../../RandomGenerator';
import { TTypeDeclaration } from '../types/TTypeDeclaration';

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
        typeParameters?: TTypeDeclaration[];
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
