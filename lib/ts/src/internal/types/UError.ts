import { UUnion } from 'uapi/internal/types/UUnion';

export class UError {
    name: string;
    errors: UUnion | any;

    constructor(name: string, errors: UUnion | any) {
        this.name = name;
        this.errors = errors;
    }
}
