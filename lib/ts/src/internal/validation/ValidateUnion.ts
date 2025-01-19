import { UStruct } from "../../internal/types/UStruct";
import { getTypeUnexpectedValidationFailure } from "../../internal/validation/GetTypeUnexpectedValidationFailure";
import { validateUnionTags } from "../../internal/validation/ValidateUnionTags";
import { ValidationFailure } from "../../internal/validation/ValidationFailure";
import { unionName } from "../types/UUnion";
import { ValidateContext } from "./ValidateContext";

export function validateUnion(
    value: any,
    name: string,
    tags: Record<string, UStruct>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === "object" && !Array.isArray(value)) {
        let selectedTags: Record<string, any>;
        if (name.startsWith("fn.")) {
            selectedTags = { [name]: ctx.select?.[name] ?? null };
        } else {
            selectedTags = ctx.select?.[name] ?? null;
        }
        return validateUnionTags(tags, selectedTags, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
