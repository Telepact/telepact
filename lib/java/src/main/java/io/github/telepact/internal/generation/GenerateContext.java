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

package io.github.telepact.internal.generation;

import io.github.telepact.RandomGenerator;

public class GenerateContext {
    public final boolean includeOptionalFields;
    public final boolean randomizeOptionalFields;
    public final boolean alwaysIncludeRequiredFields;
    public final String fnScope;
    public final RandomGenerator randomGenerator;

    public GenerateContext(boolean includeOptionalFields,
            boolean randomizeOptionalFields, boolean alwaysIncludeRequiredFields,
            String fnScope, RandomGenerator randomGenerator) {
        this.includeOptionalFields = includeOptionalFields;
        this.randomizeOptionalFields = randomizeOptionalFields;
        this.alwaysIncludeRequiredFields = alwaysIncludeRequiredFields;
        this.fnScope = fnScope;
        this.randomGenerator = randomGenerator;
    }

    public GenerateContext copyWithNewAlwaysIncludeRequiredFields(boolean alwaysIncludeRequiredFields) {
        return new GenerateContext(includeOptionalFields, randomizeOptionalFields,
                alwaysIncludeRequiredFields, fnScope, randomGenerator);
    }
}