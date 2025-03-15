import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { ValidateContext } from './ValidateContext';

export function validateStructFields(
    fields: Record<string, VFieldDeclaration>,
    selectedFields: string[] | null,
    actualStruct: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    const missingFields: string[] = [];
    for (const [fieldName, fieldDeclaration] of Object.entries(fields)) {
        const isOptional = fieldDeclaration.optional;
        const isOmittedBySelect = selectedFields !== null && !selectedFields.includes(fieldName);
        if (!(fieldName in actualStruct) && !isOptional && !isOmittedBySelect) {
            missingFields.push(fieldName);
        }
    }

    for (const missingField of missingFields) {
        const validationFailure = new ValidationFailure([], 'RequiredObjectKeyMissing', {
            key: missingField,
        });

        validationFailures.push(validationFailure);
    }

    for (const [fieldName, fieldValue] of Object.entries(actualStruct)) {
        const referenceField = fields[fieldName];
        if (referenceField === undefined) {
            const validationFailure = new ValidationFailure([fieldName], 'ObjectKeyDisallowed', {});

            validationFailures.push(validationFailure);
            continue;
        }

        const refFieldTypeDeclaration = referenceField.typeDeclaration;

        const nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, ctx);

        const nestedValidationFailuresWithPath: ValidationFailure[] = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [fieldName, ...failure.path];

            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }

        validationFailures.push(...nestedValidationFailuresWithPath);
    }

    return validationFailures;
}
