import 'package:node_interop/node.dart';
import 'package:node_interop/util.dart';
import 'dart:typed_data';

final dynamic _npmPackage = require('uapi');

class RandomGenerator {
  final dynamic _instance;

  RandomGenerator(int collectionLengthMin, int collectionLengthMax)
      : _instance =
            callConstructor(getProperty(_npmPackage, 'RandomGenerator'), [
          collectionLengthMin,
          collectionLengthMax,
        ]);

  void setSeed(int seed) {
    callMethod(_instance, 'setSeed', [seed]);
  }

  int nextInt() {
    return callMethod(_instance, 'nextInt', []);
  }

  int nextIntWithCeiling(int ceiling) {
    return callMethod(_instance, 'nextIntWithCeiling', [ceiling]);
  }

  bool nextBoolean() {
    return callMethod(_instance, 'nextBoolean', []);
  }

  String nextString() {
    return callMethod(_instance, 'nextString', []);
  }

  double nextDouble() {
    return callMethod(_instance, 'nextDouble', []);
  }

  int nextCollectionLength() {
    return callMethod(_instance, 'nextCollectionLength', []);
  }
}

class Checksum {
  final dynamic _instance;

  Checksum(String value, int expiration)
      : _instance = callConstructor(getProperty(_npmPackage, 'Checksum'), [
          value,
          expiration,
        ]);
}

abstract class ClientBinaryStrategy {
  void updateChecksum(String newChecksum);
  dynamic getCurrentChecksums();
}

class DefaultClientBinaryStrategy extends ClientBinaryStrategy {
  final dynamic _instance;

  DefaultClientBinaryStrategy()
      : _instance = callConstructor(
          getProperty(_npmPackage, 'DefaultClientBinaryStrategy'),
          [],
        );

  void updateChecksum(String newChecksum) {
    callMethod(_instance, 'updateChecksum', [newChecksum]);
  }

  dynamic getCurrentChecksums() {
    return callMethod(_instance, 'getCurrentChecksums', []);
  }
}

abstract class Serialization {
  Uint8List toJson(dynamic uapiMessage);
  Uint8List toMsgpack(dynamic uapiMessage);
  dynamic fromJson(Uint8List bytes);
  dynamic fromMsgpack(Uint8List bytes);
}

class DefaultSerialization extends Serialization {
  final dynamic _instance;

  DefaultSerialization()
      : _instance = callConstructor(
          getProperty(_npmPackage, 'DefaultSerialization'),
          [],
        );

  Uint8List toJson(dynamic uapiMessage) {
    return callMethod(_instance, 'toJson', [uapiMessage]);
  }

  Uint8List toMsgpack(dynamic uapiMessage) {
    return callMethod(_instance, 'toMsgpack', [uapiMessage]);
  }

  dynamic fromJson(Uint8List bytes) {
    return callMethod(_instance, 'fromJson', [bytes]);
  }

  dynamic fromMsgpack(Uint8List bytes) {
    return callMethod(_instance, 'fromMsgpack', [bytes]);
  }
}

class Serializer {
  final dynamic _instance;

  Serializer(DefaultSerialization serializationImpl, dynamic binaryEncoder)
      : _instance = callConstructor(getProperty(_npmPackage, 'Serializer'), [
          serializationImpl._instance,
          binaryEncoder,
        ]);

  Uint8List serialize(dynamic message) {
    return callMethod(_instance, 'serialize', [message]);
  }

  dynamic deserialize(Uint8List messageBytes) {
    return callMethod(_instance, 'deserialize', [messageBytes]);
  }
}

class Client {
  final dynamic _instance;

  Client(dynamic adapter, dynamic options)
      : _instance = callConstructor(getProperty(_npmPackage, 'Client'), [
          adapter,
          options,
        ]);

  Future<dynamic> request(dynamic requestMessage) {
    return callMethod(_instance, 'request', [requestMessage]);
  }
}

class Server {
  final dynamic _instance;

  Server(dynamic uApiSchema, dynamic handler, dynamic options)
      : _instance = callConstructor(getProperty(_npmPackage, 'Server'), [
          uApiSchema,
          handler,
          options,
        ]);

  Future<Uint8List> process(Uint8List requestMessageBytes) {
    return callMethod(_instance, 'process', [requestMessageBytes]);
  }
}

class MockServer {
  final dynamic _instance;

  MockServer(dynamic mockUApiSchema, dynamic options)
      : _instance = callConstructor(getProperty(_npmPackage, 'MockServer'), [
          mockUApiSchema,
          options,
        ]);

  Future<Uint8List> process(Uint8List message) {
    return callMethod(_instance, 'process', [message]);
  }
}

// Bindings for Message class
class Message {
  final dynamic _instance;

  Message(dynamic headers, dynamic body)
      : _instance = callConstructor(getProperty(_npmPackage, 'Message'), [
          headers,
          body,
        ]);

  dynamic getBodyTarget() {
    return callMethod(_instance, 'getBodyTarget', []);
  }

  dynamic getBodyPayload() {
    return callMethod(_instance, 'getBodyPayload', []);
  }
}

// Bindings for ValidationFailure class
class ValidationFailure {
  final dynamic _instance;

  ValidationFailure(dynamic path, String reason, dynamic data)
      : _instance = callConstructor(
          getProperty(_npmPackage, 'ValidationFailure'),
          [path, reason, data],
        );
}

// Bindings for UApiSchema class
class UApiSchema {
  final dynamic _instance;

  UApiSchema(
    dynamic original,
    dynamic full,
    dynamic parsed,
    dynamic parsedRequestHeaders,
    dynamic parsedResponseHeaders,
  ) : _instance = callConstructor(getProperty(_npmPackage, 'UApiSchema'), [
          original,
          full,
          parsed,
          parsedRequestHeaders,
          parsedResponseHeaders,
        ]);

  static UApiSchema fromJson(dynamic json) {
    return UApiSchema(
      callMethod(getProperty(_npmPackage, 'UApiSchema'), 'fromJson', [json]),
    );
  }

  static UApiSchema fromFileJsonMap(dynamic fileJsonMap) {
    return UApiSchema(
      callMethod(getProperty(_npmPackage, 'UApiSchema'), 'fromFileJsonMap', [
        fileJsonMap,
      ]),
    );
  }

  static UApiSchema fromDirectory(String directory, dynamic fs, dynamic path) {
    return UApiSchema(
      callMethod(getProperty(_npmPackage, 'UApiSchema'), 'fromDirectory', [
        directory,
        fs,
        path,
      ]),
    );
  }
}

// Bindings for UApiSchemaParseError class
class UApiSchemaParseError {
  final dynamic _instance;

  UApiSchemaParseError(
    List<dynamic> schemaParseFailures,
    Map<String, dynamic> documentNamesToJson,
    dynamic cause,
  ) : _instance = callConstructor(
          getProperty(_npmPackage, 'UApiSchemaParseError'),
          [schemaParseFailures, documentNamesToJson, cause],
        );
}

// Bindings for MockUApiSchema class
class MockUApiSchema {
  final dynamic _instance;

  MockUApiSchema(
    dynamic original,
    dynamic full,
    dynamic parsed,
    dynamic parsedRequestHeaders,
    dynamic parsedResponseHeaders,
  ) : _instance = callConstructor(getProperty(_npmPackage, 'MockUApiSchema'), [
          original,
          full,
          parsed,
          parsedRequestHeaders,
          parsedResponseHeaders,
        ]);

  static MockUApiSchema fromJson(dynamic json) {
    return MockUApiSchema(
      callMethod(getProperty(_npmPackage, 'MockUApiSchema'), 'fromJson', [
        json,
      ]),
    );
  }

  static MockUApiSchema fromFileJsonMap(dynamic jsonDocuments) {
    return MockUApiSchema(
      callMethod(
        getProperty(_npmPackage, 'MockUApiSchema'),
        'fromFileJsonMap',
        [jsonDocuments],
      ),
    );
  }

  static MockUApiSchema fromDirectory(
    String directory,
    dynamic fs,
    dynamic path,
  ) {
    return MockUApiSchema(
      callMethod(getProperty(_npmPackage, 'MockUApiSchema'), 'fromDirectory', [
        directory,
        fs,
        path,
      ]),
    );
  }
}

// Bindings for UApiSchemaFiles class
class UApiSchemaFiles {
  final dynamic _instance;

  UApiSchemaFiles(String directory, dynamic fs, dynamic path)
      : _instance =
            callConstructor(getProperty(_npmPackage, 'UApiSchemaFiles'), [
          directory,
          fs,
          path,
        ]);
}

// Bindings for BinaryEncoderUnavailableError class
class BinaryEncoderUnavailableError {
  final dynamic _instance;

  BinaryEncoderUnavailableError(String message)
      : _instance = callConstructor(
          getProperty(_npmPackage, 'BinaryEncoderUnavailableError'),
          [message],
        );
}

// Bindings for SerializationError class
class SerializationError {
  final dynamic _instance;

  SerializationError(dynamic cause)
      : _instance = callConstructor(
          getProperty(_npmPackage, 'SerializationError'),
          [cause],
        );
}

// Bindings for UApiError class
class UApiError {
  final dynamic _instance;

  UApiError(dynamic arg)
      : _instance =
            callConstructor(getProperty(_npmPackage, 'UApiError'), [arg]);
}

// Bindings for MockServerOptions class
class MockServerOptions {
  final dynamic _instance;

  MockServerOptions()
      : _instance = callConstructor(
          getProperty(_npmPackage, 'MockServerOptions'),
          [],
        );
}

// Bindings for ServerOptions class
class ServerOptions {
  final dynamic _instance;

  ServerOptions()
      : _instance = callConstructor(
          getProperty(_npmPackage, 'ServerOptions'),
          [],
        );
}

// Bindings for ClientOptions class
class ClientOptions {
  final dynamic _instance;

  ClientOptions()
      : _instance = callConstructor(
          getProperty(_npmPackage, 'ClientOptions'),
          [],
        );

  bool get useBinary => getProperty(_instance, 'useBinary');
  set useBinary(bool value) => setProperty(_instance, 'useBinary', value);

  bool get alwaysSendJson => getProperty(_instance, 'alwaysSendJson');
  set alwaysSendJson(bool value) =>
      setProperty(_instance, 'alwaysSendJson', value);

  int get timeoutMsDefault => getProperty(_instance, 'timeoutMsDefault');
  set timeoutMsDefault(int value) =>
      setProperty(_instance, 'timeoutMsDefault', value);

  DefaultSerialization get serializationImpl => DefaultSerialization()
    .._instance = getProperty(_instance, 'serializationImpl');
  set serializationImpl(DefaultSerialization value) =>
      setProperty(_instance, 'serializationImpl', value._instance);

  DefaultClientBinaryStrategy get binaryStrategy =>
      DefaultClientBinaryStrategy()
        .._instance = getProperty(_instance, 'binaryStrategy');
  set binaryStrategy(DefaultClientBinaryStrategy value) =>
      setProperty(_instance, 'binaryStrategy', value._instance);
}
