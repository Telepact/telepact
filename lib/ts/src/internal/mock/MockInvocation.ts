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
