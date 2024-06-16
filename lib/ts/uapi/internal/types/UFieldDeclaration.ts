import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';

export class UFieldDeclaration {
    field_name: string;
    type_declaration: UTypeDeclaration;
    optional: boolean;

    constructor(field_name: string, type_declaration: UTypeDeclaration, optional: boolean) {
        this.field_name = field_name;
        this.type_declaration = type_declaration;
        this.optional = optional;
    }
}
