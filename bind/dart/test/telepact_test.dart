@TestOn('browser')

import 'dart:convert';
import 'dart:js_interop';

import 'package:test/test.dart';
import 'package:telepact/telepact.dart';
import 'dart:typed_data';

extension type Window(JSObject _) implements JSObject {}

void main() {
  group('Server', () {
    test('should process request message bytes', () async {
      print('Test started');

      final telepactPseudoJson = [
        {
          "struct.Data": {
            "field": ["boolean"]
          }
        }
      ];
      print("Encoding json");
      final telepactJson = jsonEncode(telepactPseudoJson);
      print('Creating TelepactSchema');
      final telepactSchema = TelepactSchema.fromJson(telepactJson);
      print('TelepactSchema created: $telepactSchema');

      JSPromise handler(Message requestMessage) {
        print('Handler called with requestMessage: $requestMessage');
        return Future.value(Message(JSObject(), JSObject())).toJS;
      }

      print('Creating ServerOptions');
      final serverOptions = ServerOptions()..authRequired = false;
      print('ServerOptions created: $serverOptions');

      print('Creating Server');
      final server = Server(telepactSchema, handler.toJS, serverOptions);
      print('Server created: $server');

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      print('Request message bytes: $requestMessageBytes');

      dynamic request = [
        {},
        {"fn.ping_": {}}
      ];
      dynamic requestJson = jsonEncode(request);
      print('Request bytes: $requestJson');

      final requestBytes = Uint8List.fromList(utf8.encode(requestJson));

      print('Processing request');
      final responseBytes = await server.process(requestBytes.toJS).toDart;
      print('Response bytes: $responseBytes');

      dynamic response = jsonDecode(utf8.decode(responseBytes.toDart));
      print('Response: $response');

      dynamic expectedResponse = [
        {},
        {"Ok_": {}}
      ];
      print('Expected response: $expectedResponse');

      expect(response, equals(expectedResponse));
      print('Test completed');
    });
  });
}
