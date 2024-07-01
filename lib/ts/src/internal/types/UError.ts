import { UUnion } from '../../internal/types/UUnion';

export class UError {
    name: string;
    errors: UUnion;

    constructor(name: string, errors: UUnion) {
        this.name = name;
        this.errors = errors;
    }
}
