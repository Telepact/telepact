package io.github.brenbar.japi.server;

import io.github.brenbar.japi.BinaryEncoder;

import java.util.*;
import java.util.function.Consumer;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

class ProcessObject {

    static List<Object> process(List<Object> inputJapiMessage, Consumer<Throwable> onError, BinaryEncoder binaryEncoder,
            Map<String, Definition> apiDescription, Handler internalHandler, Handler handler) {
        var finalHeaders = new HashMap<String, Object>();
        try {
            try {
                if (inputJapiMessage.size() < 3) {
                    throw new Error.JapiMessageArrayTooFewElements();
                }

                String messageType;
                try {
                    messageType = (String) inputJapiMessage.get(0);
                } catch (ClassCastException e) {
                    throw new Error.JapiMessageTypeNotString();
                }

                var regex = Pattern.compile("^function\\.([a-zA-Z_]\\w*)(.input)?");
                var matcher = regex.matcher(messageType);
                if (!matcher.matches()) {
                    throw new Error.JapiMessageTypeNotFunction();
                }
                var functionName = matcher.group(1);

                Map<String, Object> headers;
                try {
                    headers = (Map<String, Object>) inputJapiMessage.get(1);
                } catch (ClassCastException e) {
                    throw new Error.JapiMessageHeaderNotObject();
                }

                if (Objects.equals(headers.get("_binaryStart"), true)) {
                    // Client is initiating handshake for binary protocol
                    finalHeaders.put("_bin", binaryEncoder.binaryHash);
                    finalHeaders.put("_binaryEncoding", binaryEncoder.encodeMap);
                }

                // Reflect call id
                var callId = headers.get("_id");
                if (callId != null) {
                    finalHeaders.put("_id", callId);
                }

                Map<String, Object> input;
                try {
                    input = (Map<String, Object>) inputJapiMessage.get(2);
                } catch (ClassCastException e) {
                    throw new Error.JapiMessageBodyNotObject();
                }

                var functionDef = apiDescription.get(messageType);

                FunctionDefinition functionDefinition;
                if (functionDef instanceof FunctionDefinition f) {
                    functionDefinition = f;
                } else {
                    throw new Error.FunctionNotFound(functionName);
                }

                Map<String, List<String>> slicedTypes = null;
                if (headers.containsKey("_selectFields")) {
                    try {
                        slicedTypes = (Map<String, List<String>>) headers.get("_selectFields");
                        for (Map.Entry<String, List<String>> entry : slicedTypes.entrySet()) {
                            var fields = entry.getValue();
                            for (var field : fields) {
                                // verify the cast works
                                var stringField = (String) field;
                            }
                        }
                    } catch (ClassCastException e) {
                        throw new Error.InvalidSelectFieldsHeader();
                    }
                }

                ValidateStruct.validate("input", functionDefinition.inputStruct().fields(), input);

                Map<String, Object> output;
                try {
                    if (functionName.startsWith("_")) {
                        output = internalHandler.handle(functionName, headers, input);
                    } else {
                        output = handler.handle(functionName, headers, input);
                    }
                } catch (Error.ApplicationFailure e) {
                    if (functionDefinition.errors().contains(e.messageType)) {
                        var def = (ErrorDefinition) apiDescription.get(e.messageType);
                        try {
                            ValidateStruct.validate("error", def.fields(), e.body);
                        } catch (Exception e2) {
                            throw new Error.InvalidApplicationFailure(e2);
                        }

                        throw e;
                    } else {
                        throw new Error.DisallowedError(e);
                    }
                }

                try {
                    ValidateStruct.validate("output", functionDefinition.outputStruct().fields(), output);
                } catch (Exception e) {
                    throw new Error.InvalidOutput(e);
                }

                Map<String, Object> finalOutput;
                if (slicedTypes != null) {
                    finalOutput = (Map<String, Object>) SliceTypes.sliceTypes(functionDefinition.outputStruct(), output,
                            slicedTypes);
                } else {
                    finalOutput = output;
                }

                var outputMessageType = "function.%s".formatted(functionName);

                return List.of(outputMessageType, finalHeaders, finalOutput);
            } catch (Exception e) {
                try {
                    onError.accept(e);
                } catch (Exception ignored) {
                }
                throw e;
            }
        } catch (Error.StructHasExtraFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.extraFields.stream()
                    .collect(Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "UnknownStructField"));
            var messageBody = CreateInvalidFields.createInvalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (Error.StructMissingFields e) {
            var messageType = "error._InvalidInput";
            var errors = e.missingFields.stream().collect(
                    Collectors.toMap(f -> "%s.%s".formatted(e.namespace, f), f -> "RequiredStructFieldMissing"));
            var messageBody = CreateInvalidFields.createInvalidFields(errors);

            return List.of(messageType, finalHeaders, messageBody);

        } catch (Error.UnknownEnumField e) {
            var messageType = "error._InvalidInput";
            var messageBody = CreateInvalidFields.createInvalidField("%s.%s".formatted(e.namespace, e.field),
                    "UnknownEnumField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (Error.EnumDoesNotHaveOnlyOneField e) {
            var messageType = "error._InvalidInput";
            var messageBody = CreateInvalidFields.createInvalidField(e.namespace, "EnumDoesNotHaveExactlyOneField");

            return List.of(messageType, finalHeaders, messageBody);
        } catch (Error.InvalidFieldType e) {
            var entry = CreateInvalidFields.createInvalidField(e);

            var messageType = entry.getKey();
            var messageBody = entry.getValue();

            return List.of(messageType, finalHeaders, messageBody);
        } catch (Error.InvalidOutput | Error.InvalidApplicationFailure e) {
            var messageType = "error._InvalidOutput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (Error.InvalidInput e) {
            var messageType = "error._InvalidInput";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (Error.InvalidBinaryEncoding | Error.BinaryDecodeFailure e) {
            var messageType = "error._InvalidBinary";

            finalHeaders.put("_binaryEncoding", binaryEncoder.encodeMap);

            return List.of(messageType, finalHeaders, Map.of());
        } catch (Error.FunctionNotFound e) {
            var messageType = "error._UnknownFunction";

            return List.of(messageType, finalHeaders, Map.of());
        } catch (Error.ApplicationFailure e) {
            var messageType = e.messageType;

            return List.of(messageType, finalHeaders, e.body);
        } catch (Exception e) {
            var messageType = "error._ApplicationFailure";

            return List.of(messageType, finalHeaders, Map.of());
        }
    };
}
