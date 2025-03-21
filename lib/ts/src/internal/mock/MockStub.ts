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

export class MockStub {
    public whenFunction: string;
    public whenArgument: Record<string, any>;
    public thenResult: Record<string, any>;
    public allowArgumentPartialMatch: boolean;
    public count: number;

    constructor(
        whenFunction: string,
        whenArgument: Record<string, any>,
        thenResult: Record<string, any>,
        allowArgumentPartialMatch: boolean,
        count: number,
    ) {
        this.whenFunction = whenFunction;
        this.whenArgument = whenArgument;
        this.thenResult = thenResult;
        this.allowArgumentPartialMatch = allowArgumentPartialMatch;
        this.count = count;
    }
}
