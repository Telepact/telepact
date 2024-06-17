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
