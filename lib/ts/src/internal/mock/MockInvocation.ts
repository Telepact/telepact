//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export class MockInvocation {
    functionName: string;
    functionArgument: Record<string, any>;
    verified: boolean;

    constructor(functionName: string, functionArgument: Record<string, any>) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
        this.verified = false;
    }
}
