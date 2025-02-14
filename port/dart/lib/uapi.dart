@JS()
library uapi;

import 'package:js/js.dart';
import 'dart:typed_data';

@JS('uapi.RandomGenerator')
class RandomGenerator {
  external int seed;
  external int collectionLengthMin;
  external int collectionLengthMax;
  external int count;

  external RandomGenerator(int collectionLengthMin, int collectionLengthMax);
  external void setSeed(int seed);
  external int nextInt();
  external int nextIntWithCeiling(int ceiling);
  external bool nextBoolean();
  external String nextString();
  external double nextDouble();
  external int nextCollectionLength();
}

@JS('uapi.Checksum')
class Checksum {
  external String value;
  external int expiration;

  external Checksum(String value, int expiration);
}

@JS('uapi.DefaultClientBinaryStrategy')
class DefaultClientBinaryStrategy {
  external Checksum primary;
  external Checksum secondary;
  external DateTime lastUpdate;

  external DefaultClientBinaryStrategy();
  external void updateChecksum(String newChecksum);
  external List<Checksum> getCurrentChecksums();
}

@JS('uapi.Message')
class Message {
  external Map<String, dynamic> headers;
  external Map<String, dynamic> body;

  external Message(Map<String, dynamic> headers, Map<String, dynamic> body);
  external String getBodyTarget();
  external dynamic getBodyPayload();
}

@JS('uapi.DefaultSerialization')
class DefaultSerialization {
  external DefaultSerialization();
  external Uint8List toJson(dynamic uapiMessage);
  external Uint8List toMsgpack(dynamic uapiMessage);
  external dynamic fromJson(Uint8List bytes);
  external dynamic fromMsgpack(Uint8List bytes);
}

@JS('uapi.Serializer')
class Serializer {
  external Serializer(
      DefaultSerialization serializationImpl, dynamic binaryEncoder);
  external Uint8List serialize(Message message);
  external Message deserialize(Uint8List messageBytes);
}

@JS('uapi.Client')
class Client {
  external Client(dynamic adapter, dynamic options);
  external Future<Message> request(Message requestMessage);
}

@JS('uapi.Server')
class Server {
  external Server(dynamic uApiSchema, dynamic handler, dynamic options);
  external Future<Uint8List> process(Uint8List requestMessageBytes);
}

@JS('uapi.ServerOptions')
class ServerOptions {
  external ServerOptions();
  external void setOnError(Function onError);
  external void setOnRequest(Function onRequest);
  external void setOnResponse(Function onResponse);
  external void setAuthRequired(bool authRequired);
  external void setSerialization(DefaultSerialization serialization);
}

@JS('uapi.UApiSchema')
class UApiSchema {
  external UApiSchema(dynamic original, dynamic full, dynamic parsed,
      dynamic parsedRequestHeaders, dynamic parsedResponseHeaders);
  external static UApiSchema fromJson(String json);
  external static UApiSchema fromFileJsonMap(Map<String, String> fileJsonMap);
  external static UApiSchema fromDirectory(
      String directory, dynamic fs, dynamic path);
}

@JS('uapi.MockServer')
class MockServer {
  external MockServer(dynamic mockUApiSchema, dynamic options);
  external Future<Uint8List> process(Uint8List message);
}

@JS('uapi.MockServerOptions')
class MockServerOptions {
  external MockServerOptions();
  external void setOnError(Function onError);
  external void setEnableMessageResponseGeneration(bool enable);
  external void setEnableOptionalFieldGeneration(bool enable);
  external void setRandomizeOptionalFieldGeneration(bool enable);
  external void setGeneratedCollectionLengthMin(int min);
  external void setGeneratedCollectionLengthMax(int max);
}

@JS('uapi.MockUApiSchema')
class MockUApiSchema {
  external MockUApiSchema(dynamic original, dynamic full, dynamic parsed,
      dynamic parsedRequestHeaders, dynamic parsedResponseHeaders);
  external static MockUApiSchema fromJson(String json);
  external static MockUApiSchema fromFileJsonMap(
      Map<String, String> fileJsonMap);
  external static MockUApiSchema fromDirectory(
      String directory, dynamic fs, dynamic path);
}

@JS('uapi.ClientBinaryEncoder')
class ClientBinaryEncoder {
  external ClientBinaryEncoder(dynamic binaryChecksumStrategy);
  external dynamic encode(dynamic message);
  external dynamic decode(dynamic message);
}

@JS('uapi.ServerBinaryEncoder')
class ServerBinaryEncoder {
  external ServerBinaryEncoder(dynamic binaryEncoder);
  external dynamic encode(dynamic message);
  external dynamic decode(dynamic message);
}

@JS('uapi.BinaryEncoding')
class BinaryEncoding {
  external BinaryEncoding(dynamic binaryEncodingMap, int checksum);
}

@JS('uapi.MockInvocation')
class MockInvocation {
  external String functionName;
  external dynamic functionArgument;
  external bool verified;

  external MockInvocation(String functionName, dynamic functionArgument);
}

@JS('uapi.MockStub')
class MockStub {
  external String whenFunction;
  external dynamic whenArgument;
  external dynamic thenResult;
  external bool allowArgumentPartialMatch;
  external int count;

  external MockStub(String whenFunction, dynamic whenArgument,
      dynamic thenResult, bool allowArgumentPartialMatch, int count);
}

@JS('uapi.ClientBinaryStrategy')
class ClientBinaryStrategy {
  external ClientBinaryStrategy();
}

@JS('uapi.UApiSchemaFiles')
class UApiSchemaFiles {
  external UApiSchemaFiles(String directory, dynamic fs, dynamic path);
  external Map<String, String> get filenamesToJson;
}

@JS('uapi.UApiSchemaParseError')
class UApiSchemaParseError {
  external List<dynamic> schemaParseFailures;
  external List<dynamic> schemaParseFailuresPseudoJson;

  external UApiSchemaParseError(List<dynamic> schemaParseFailures,
      Map<String, String> documentNamesToJson, dynamic cause);
}

@JS('uapi.SerializationError')
class SerializationError {
  external SerializationError(dynamic cause);
}

@JS('uapi.UApiError')
class UApiError {
  external UApiError(dynamic arg);
}

@JS('uapi.ValidationFailure')
class ValidationFailure {
  external String path;
  external String reason;
  external dynamic data;

  external ValidationFailure(String path, String reason, dynamic data);
}

@JS('uapi.InvalidMessage')
class InvalidMessage {
  external InvalidMessage(dynamic cause);
}

@JS('uapi.InvalidMessageBody')
class InvalidMessageBody {
  external InvalidMessageBody();
}

@JS('uapi.BinaryEncoderUnavailableError')
class BinaryEncoderUnavailableError {
  external BinaryEncoderUnavailableError();
}

@JS('uapi.BinaryEncodingMissing')
class BinaryEncodingMissing {
  external BinaryEncodingMissing(dynamic key);
}
