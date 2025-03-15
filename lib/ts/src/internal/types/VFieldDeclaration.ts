import { VTypeDeclaration } from './VTypeDeclaration';

export class VFieldDeclaration {
    fieldName: string;
    typeDeclaration: VTypeDeclaration;
    optional: boolean;

    constructor(fieldName: string, typeDeclaration: VTypeDeclaration, optional: boolean) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
