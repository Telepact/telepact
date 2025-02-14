import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'dart:vmservice_io';
import 'package:uapi/uapi.dart';
import 'dart:typed_data';
import 'nats_wrapped.dart';

Future<Subscription> startClientTestServer(
    NatsConnection connection,
    String clientFrontdoorTopic,
    String clientBackdoorTopic,
    bool defaultBinary,
    bool useCodegen) async {
  final adapter = (Message m, Serializer s) async {
    try {
      Uint8List requestBytes;
      try {
        requestBytes = s.serialize(m);
      } catch (e) {
        if (e is SerializationError) {
          return Message({'numberTooBig': true}, {'ErrorUnknown_': {}});
        } else {
          throw e;
        }
      }

      print('   <-c  ${utf8.decode(requestBytes)}');
      final natsResponseMessage = await connection.request(clientBackdoorTopic, requestBytes, timeout: Duration(seconds: 5));
      final responseBytes = natsResponseMessage.data;

      print('   ->c  ${utf8.decode(responseBytes)}');

      final responseMessage = s.deserialize(responseBytes);
      return responseMessage;
    } catch (e) {
      print(e);
      throw e;
    }
  };

  final options = ClientOptions()
    ..useBinary = defaultBinary
    ..alwaysSendJson = !defaultBinary;
  final client = Client(adapter, options);

  final genClient = ClientInterface_(client);

  final sub = await connection.subscribe(clientFrontdoorTopic);

  sub.stream.listen((msg) async {
    final requestBytes = msg.data;
    final requestJson = utf8.decode(requestBytes);

    print('   ->C  $requestJson');

    final requestPseudoJson = jsonDecode(requestJson);
    final requestHeaders = requestPseudoJson[0] as Map<String, dynamic>;
    final requestBody = requestPseudoJson[1] as Map<String, dynamic>;
    final request = Message(requestHeaders, requestBody);

    final entry = requestBody.entries.first;
    final functionName = entry.key;
    final argument = entry.value;

    Message response;
    try {
      if (useCodegen && functionName == 'fn.test') {
        final result = await genClient.test(requestHeaders, test.Input(requestBody));
        final responseHeaders = result[0];
        final outputBody = result[1];
        responseHeaders['_codegenc'] = true;
        response = Message(responseHeaders, outputBody.pseudoJson);
      } else {
        response = await client.request(request);
      }
    } finally {
    }

    final responsePseudoJson = [response.headers, response.body];
    final responseJson = jsonEncode(responsePseudoJson);
    final responseBytes = utf8.encode(responseJson);

    print('   <-C  ${utf8.decode(responseBytes)}');

    msg.respond(responseBytes);
  });

  return sub;
}

Future<Subscription> startMockTestServer(
    NatsConnection connection,
    String apiSchemaPath,
    String frontdoorTopic,
    Map<String, dynamic> config) async {
  final uApi = MockUApiSchema.fromDirectory(apiSchemaPath, FileSystemEntity, path);

  final options = MockServerOptions()
    ..onError = (e) => print(e)
    ..enableMessageResponseGeneration = false;

  if (config != null) {
    options
      ..generatedCollectionLengthMin = config['minLength']
      ..generatedCollectionLengthMax = config['maxLength']
      ..enableMessageResponseGeneration = config['enableGen'];
  }

  final server = MockServer(uApi, options);

  final subscription = await connection.subscribe(frontdoorTopic);
  subscription.stream.listen((msg) async {
    final requestBytes = msg.data;

    print('    ->S ${utf8.decode(requestBytes)}');

    Uint8List responseBytes;
    try {
      responseBytes = await server.process(requestBytes);
    } finally {
    }

    print('    <-S ${utf8.decode(responseBytes)}');

    msg.respond(responseBytes);
  });

  return subscription;
}

Future<Subscription> startSchemaTestServer(
    NatsConnection connection,
    String apiSchemaPath,
    String frontdoorTopic) async {
  final uApi = UApiSchema.fromDirectory(apiSchemaPath, FileSystemEntity, path);

  final handler = (Message requestMessage) async {
    final requestBody = requestMessage.body;

    final arg = requestBody['fn.validateSchema'];
    final input = arg['input'];
    final inputTag = input.keys.first;

    try {
      if (inputTag == 'PseudoJson') {
        final unionValue = input[inputTag];
        final schemaJson = unionValue['schema'];
        final extendJson = unionValue['extend!'];

        if (extendJson != null) {
          UApiSchema.fromFileJsonMap({'default': schemaJson, 'extend': extendJson});
        } else {
          UApiSchema.fromJson(schemaJson);
        }
      } else if (inputTag == 'Json') {
        final unionValue = input[inputTag];
        final schemaJson = unionValue['schema'];
        UApiSchema.fromJson(schemaJson);
      } else if (inputTag == 'Directory') {
        final unionValue = input[inputTag];
        final schemaDirectory = unionValue['schemaDirectory'];
        UApiSchema.fromDirectory(schemaDirectory, FileSystemEntity, path);
      } else {
        throw Exception('Invalid input tag');
      }
    } catch (e) {
      print(e);
      return Message({}, {'ErrorValidationFailure': {'cases': (e as UApiSchemaParseError).schemaParseFailuresPseudoJson}});
    }

    return Message({}, {'Ok_': {}});
  };

  final options = ServerOptions()
    ..onError = (e) => print(e)
    ..authRequired = false;

  final server = Server(uApi, handler, options);

  final subscription = await connection.subscribe(frontdoorTopic);
  subscription.stream.listen((msg) async {
    final requestBytes = msg.data;

    print('    ->S ${utf8.decode(requestBytes)}');

    Uint8List responseBytes;
    try {
      responseBytes = await server.process(requestBytes);
    } finally {
    }

    print('    <-S ${utf8.decode(responseBytes)}');

    msg.respond(responseBytes);
  });

  return subscription;
}

Future<Subscription> startTestServer(
    NatsConnection connection,
    String apiSchemaPath,
    String frontdoorTopic,
    String backdoorTopic,
    bool authRequired,
    bool useCodegen) async {
  final files = UApiSchemaFiles(apiSchemaPath, FileSystemEntity, path);
  final alternateMap = Map<String, String>.from(files.filenamesToJson);
  alternateMap['backwardsCompatibleChange'] = '''
    [
      {
        "struct.BackwardsCompatibleChange": {}
      }
    ]
  ''';

  final uApi = UApiSchema.fromFileJsonMap(files.filenamesToJson);
  final alternateUApi = UApiSchema.fromFileJsonMap(alternateMap);

  final serveAlternateServer = ValueNotifier<bool>(false);

  final codeGenHandler = CodeGenHandler();

  class ThisError implements Exception {}

  final handler = (Message requestMessage) async {
    final requestHeaders = requestMessage.headers;
    final requestBody = requestMessage.body;
    final requestPseudoJson = [requestHeaders, requestBody];
    final requestJson = jsonEncode(requestPseudoJson);
    final requestBytes = utf8.encode(requestJson);

    Message message;
    if (useCodegen) {
      print('     :H ${utf8.decode(requestBytes)}');
      message = await codeGenHandler.handler(requestMessage);
      message.headers['_codegens'] = true;
    } else {
      print('    <-s ${utf8.decode(requestBytes)}');
      final natsResponseMessage = await connection.request(backdoorTopic, requestBytes, timeout: Duration(seconds: 5));

      print('    ->s ${utf8.decode(natsResponseMessage.data)}');

      final responseJson = utf8.decode(natsResponseMessage.data);
      final responsePseudoJson = jsonDecode(responseJson);
      final responseHeaders = responsePseudoJson[0] as Map<String, dynamic>;
      final responseBody = responsePseudoJson[1] as Map<String, dynamic>;

      message = Message(responseHeaders, responseBody);
    }

    if (requestHeaders['_toggleAlternateServer'] == true) {
      serveAlternateServer.value = !serveAlternateServer.value;
    }

    if (requestHeaders['_throwError'] == true) {
      throw ThisError();
    }

    return message;
  };

  final options = ServerOptions()
    ..onError = (e) {
      print(e);
      if (e is ThisError) {
        throw Exception();
      }
    }
    ..onRequest = (m) {
      if (m.headers['_onRequestError'] == true) {
        throw Exception();
      }
    }
    ..onResponse = (m) {
      if (m.headers['_onResponseError'] == true) {
        throw Exception();
      }
    }
    ..authRequired = authRequired;

  final server = Server(uApi, handler, options);

  final alternateOptions = ServerOptions()
    ..onError = (e) => print(e)
    ..authRequired = authRequired;
  final alternateServer = Server(alternateUApi, handler, alternateOptions);

  final subscription = await connection.subscribe(frontdoorTopic);
  subscription.stream.listen((msg) async {
    final requestBytes = msg.data;

    print('    ->S ${utf8.decode(requestBytes)}');
    Uint8List responseBytes;
    try {
      if (serveAlternateServer.value) {
        responseBytes = await alternateServer.process(requestBytes);
      } else {
        responseBytes = await server.process(requestBytes);
      }
    } finally {
    }

    print('    <-S ${utf8.decode(responseBytes)}');

    msg.respond(responseBytes);
  });

  print('Test server listening on $frontdoorTopic');

  return subscription;
}

Future<void> runDispatcherServer() async {
  final natsUrl = Platform.environment['NATS_URL'];
  if (natsUrl == null) {
    throw Exception('NATS_URL env var not set');
  }

  final servers = <String, Subscription>{};

  final natsOpts = ConnectionOptions(servers: natsUrl);
  final connection = await connect(natsOpts);

  final done = Completer<void>();
  final subscription = await connection.subscribe('ts', SubscriptionOptions());

  await for (final msg in subscription) {
    final requestBytes = msg.data;
    final requestJson = utf8.decode(requestBytes);

    print('    ->S $requestJson');

    Uint8List responseBytes;
    try {
      final request = jsonDecode(requestJson);
      final body = request[1];
      final entry = body.entries.first;
      final target = entry.key;
      final payload = entry.value as Map<String, dynamic>;

      switch (target) {
        case 'Ping':
          break;
        case 'End':
          done.complete();
          break;
        case 'Stop':
          final id = payload['id'] as String;
          final s = servers[id];
          if (s != null) {
            await s.drain();
          }
          break;
        case 'StartServer':
          final id = payload['id'] as String;
          final apiSchemaPath = payload['apiSchemaPath'] as String;
          final frontdoorTopic = payload['frontdoorTopic'] as String;
          final backdoorTopic = payload['backdoorTopic'] as String;
          final authRequired = payload['authRequired!'] ?? false;
          final useCodegen = payload['useCodeGen'] ?? false;

          final d = await startTestServer(
              connection, apiSchemaPath, frontdoorTopic, backdoorTopic, authRequired, useCodegen);

          servers[id] = d;
          break;
        case 'StartClientServer':
          final id = payload['id'] as String;
          final clientFrontdoorTopic = payload['clientFrontdoorTopic'] as String;
          final clientBackdoorTopic = payload['clientBackdoorTopic'] as String;
          final useBinary = payload['useBinary'] ?? false;
          final useCodegen = payload['useCodeGen'] ?? false;

          final d = await startClientTestServer(
              connection, clientFrontdoorTopic, clientBackdoorTopic, useBinary, useCodegen);

          servers[id] = d;
          break;
        case 'StartMockServer':
          final id = payload['id'] as String;
          final apiSchemaPath = payload['apiSchemaPath'] as String;
          final frontdoorTopic = payload['frontdoorTopic'] as String;
          final config = payload['config'] as Map<String, dynamic>;
          final d = await startMockTestServer(connection, apiSchemaPath, frontdoorTopic, config);

          servers[id] = d;
          break;
        case 'StartSchemaServer':
          final id = payload['id'] as String;
          final apiSchemaPath = payload['apiSchemaPath'] as String;
          final frontdoorTopic = payload['frontdoorTopic'] as String;
          final d = await startSchemaTestServer(connection, apiSchemaPath, frontdoorTopic);

          servers[id] = d;
          break;
        default:
          throw Exception('no matching server');
      }

      final responseJson = jsonEncode([{}, {'Ok_': {}}]);
      responseBytes = utf8.encode(responseJson);
    } catch (e) {
      print(e);
      try {
        final responseJson = jsonEncode([{}, {'ErrorUnknown': {}}]);
        responseBytes = utf8.encode(responseJson);
      } catch (e1) {
        throw Exception();
      }
    }

    print('    <-S ${utf8.decode(responseBytes)}');

    msg.respond(responseBytes);
  });

  await done.future;

  print('Dispatcher exiting');
}

Future<void> main() async {
  await runDispatcherServer();
}
