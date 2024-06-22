import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';

export class UFieldDeclaration {
    fieldName: string;
    typeDeclaration: UTypeDeclaration;
    optional: boolean;

    constructor(fieldName: string, typeDeclaration: UTypeDeclaration, optional: boolean) {
        this.fieldName = fieldName;
        this.typeDeclaration = typeDeclaration;
        this.optional = optional;
    }
}
