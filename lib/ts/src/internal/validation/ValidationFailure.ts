export class ValidationFailure {
    constructor(
        public path: any[],
        public reason: string,
        public data: Record<string, any>,
    ) {}
}
