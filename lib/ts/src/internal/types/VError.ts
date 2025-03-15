import { VUnion } from './VUnion';

export class VError {
    name: string;
    errors: VUnion;

    constructor(name: string, errors: VUnion) {
        this.name = name;
        this.errors = errors;
    }
}
