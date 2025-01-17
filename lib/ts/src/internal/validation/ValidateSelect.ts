import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';

export function validateSelect(givenObj: any, fn: string, possibleFnSelects: Record<string, any>): ValidationFailure[] {
    if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null || givenObj === undefined) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const possibleSelect = possibleFnSelects[fn] as Record<string, any>;

    return isSubSelect([], givenObj, possibleSelect);
}

function isSubSelect(path: any[], givenObj: any, possibleSelectSection: any): ValidationFailure[] {
    console.log(
        `validating ${path.join('.')} with givenObject: ${JSON.stringify(givenObj)} and possibleSelectSection: ${JSON.stringify(possibleSelectSection)}`,
    );
    if (Array.isArray(possibleSelectSection)) {
        if (!Array.isArray(givenObj)) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Array');
        }

        const validationFailures: ValidationFailure[] = [];

        for (const [index, element] of givenObj.entries()) {
            if (!possibleSelectSection.includes(element)) {
                validationFailures.push(new ValidationFailure([...path, index], 'ArrayElementDisallowed', {}));
            }
        }

        return validationFailures;
    } else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Object');
        }

        const validationFailures: ValidationFailure[] = [];

        for (const [key, value] of Object.entries(givenObj)) {
            if (key in possibleSelectSection) {
                const innerFailures = isSubSelect([...path, key], value, possibleSelectSection[key]);
                validationFailures.push(...innerFailures);
            } else {
                validationFailures.push(new ValidationFailure([...path, key], 'ObjectKeyDisallowed', {}));
            }
        }

        return validationFailures;
    }

    return [];
}
