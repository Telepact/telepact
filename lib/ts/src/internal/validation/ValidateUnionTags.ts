import { ValidationFailure } from "../../internal/validation/ValidationFailure";
import { UStruct } from "../../internal/types/UStruct";
import { getTypeUnexpectedValidationFailure } from "../../internal/validation/GetTypeUnexpectedValidationFailure";
import { validateUnionStruct } from "../../internal/validation/ValidateUnionStruct";
import { ValidateContext } from "./ValidateContext";

export function validateUnionTags(
    referenceTags: Record<string, UStruct>,
    selectedTags: Record<string, any>,
    actual: Record<any, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (Object.keys(actual).length !== 1) {
        return [
            new ValidationFailure([], "ObjectSizeUnexpected", {
                actual: Object.keys(actual).length,
                expected: 1,
            }),
        ];
    }

    const [unionTarget, unionPayload] = Object.entries(actual)[0];

    const referenceStruct = referenceTags[unionTarget];
    if (referenceStruct === undefined) {
        return [new ValidationFailure([unionTarget], "ObjectKeyDisallowed", {})];
    }

    if (typeof unionPayload === "object" && !Array.isArray(unionPayload)) {
        const nestedValidationFailures = validateUnionStruct(
            referenceStruct,
            unionTarget,
            unionPayload,
            selectedTags,
            ctx,
        );

        const nestedValidationFailuresWithPath: ValidationFailure[] = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [unionTarget, ...failure.path];
            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }

        return nestedValidationFailuresWithPath;
    } else {
        return getTypeUnexpectedValidationFailure([unionTarget], unionPayload, "Object");
    }
}
