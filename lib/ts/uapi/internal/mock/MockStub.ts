export class MockStub {
    private whenFunction: string;
    private whenArgument: Record<string, any>;
    private thenResult: Record<string, any>;
    private allowArgumentPartialMatch: boolean;
    private count: number;

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
