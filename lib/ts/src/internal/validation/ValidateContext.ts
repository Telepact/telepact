export class ValidateContext {
    select: { [key: string]: any } | null;
    fn: string | null;

    constructor(select: { [key: string]: any } | null, fn: string | null) {
        this.select = select;
        this.fn = fn;
    }
}
