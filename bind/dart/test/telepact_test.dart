//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

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
          "fn.add": {
            "x": ["integer"],
            "y": ["integer"]
          },
          "->": [
            {
              "Ok_": {
                "result": ["integer"]
              }
            }
          ]
        }
      ];
      print("Encoding json");
      final telepactJson = jsonEncode(telepactPseudoJson);
      print('Creating TelepactSchema');
      final telepactSchema = TelepactSchema.fromJson(telepactJson);
      print('TelepactSchema created: $telepactSchema');

   

      JSPromise handler(Message requestMessage) {
        final body = requestMessage.body.dartify() as Map<String, Object>;
        final x = body['x'] as int;
        final y = body['y'] as int;
        final result = x + y;
        final response = Message(
          {}.jsify(),
          {"Ok_": {"result": result}}.jsify()
        );
        return Future.value(response).toJS;
      }

      print('Creating ServerOptions');
      final serverOptions = ServerOptions()..authRequired = false;
      print('ServerOptions created: $serverOptions');

      print('Creating Server');
      final server = Server(telepactSchema, handler.toJS, serverOptions);
      print('Server created: $server');

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      print('Request message bytes: $requestMessageBytes');

      JSPromise adapter(Message m, Serializer s) {
        final requestBytes = s.serialize(m);
        final responseBytes = server.process(requestBytes).toDart;
        return responseBytes.then((value) {
          final response = s.deserialize(value);
          return response.jsify();
        }).toJS;
      }

      final clientOptions = ClientOptions()..useBinary = true;
      final client = Client(adapter.toJS, clientOptions);

      // dynamic request = [
      //   {},
      //   {"fn.ping_": {}}
      // ];
      // dynamic requestJson = jsonEncode(request);
      // print('Request bytes: $requestJson');

      final request = Message(
        {}.jsify(),
        {'fn.ping_': {}}.jsify()
      );

      var response = await client.request(request).toDart;

      // final requestBytes = Uint8List.fromList(utf8.encode(requestJson));

      // print('Processing request');
      // final responseBytes = await server.process(requestBytes.toJS).toDart;
      // print('Response bytes: $responseBytes');

      // dynamic response = jsonDecode(utf8.decode(responseBytes.toDart));
      // print('Response: $response');

      Message expectedResponse = Message(
        {
          '@enc_': {
            'Ok_': 0,
            'api': 1,
            'fn.add': 2,
            'fn.api_': 3,
            'fn.ping_': 4,
            'result': 5,
            'x': 6,
            'y': 7
          },
          '@bin_': [-2064039486]
        }.jsify(),
        {"Ok_": {}}.jsify()
      );
      print('Expected response: $expectedResponse');

      // Print contents and type
      print(response.body.dartify());
      print(response.body.dartify().runtimeType);

      expect(response.headers.dartify(), equals(expectedResponse.headers.dartify()));
      expect(response.body.dartify(), equals(expectedResponse.body.dartify()));

      print('Test completed');
    }, skip: true);

    test('should work e2e from client to server', () async {
      final telepactPseudoJson = [
        {
          "fn.add": {
            "x": ["integer"],
            "y": ["integer"]
          },
          "->": [
            {
              "Ok_": {
                "result": ["integer"]
              }
            }
          ]
        }
      ];
      final telepactJson = jsonEncode(telepactPseudoJson);
      final telepactSchema = TelepactSchema.fromJson(telepactJson);

      JSPromise handler(Message requestMessage) {
        final body = requestMessage.body.dartify() as Map<String, Object>;
        final x = body['x'] as int;
        final y = body['y'] as int;
        final result = x + y;
        final response = Message(
          {}.jsify(),
          {"Ok_": {"result": result}}.jsify()
        );
        return Future.value(response).toJS;
      }

      final serverOptions = ServerOptions()..authRequired = false;
      final server = Server(telepactSchema, handler.toJS, serverOptions);

      JSPromise adapter(Message m, Serializer s) {
        final requestBytes = s.serialize(m);
        final responseBytes = server.process(requestBytes).toDart;
        return responseBytes.then((value) {
          final response = s.deserialize(value);
          return response.jsify();
        }).toJS;
      }

      final clientOptions = ClientOptions()..useBinary = true;
      final client = Client(adapter.toJS, clientOptions);

      final request = Message(
        {}.jsify(),
        {'fn.ping_': {}}.jsify()
      );

      var response = await client.request(request).toDart;

      Message expectedResponse = Message(
        {
          '@enc_': {
            'Ok_': 0,
            'api': 1,
            'fn.add': 2,
            'fn.api_': 3,
            'fn.ping_': 4,
            'result': 5,
            'x': 6,
            'y': 7
          },
          '@bin_': [-2064039486]
        }.jsify(),
        {"Ok_": {}}.jsify()
      );

      expect(response.headers.dartify(), equals(expectedResponse.headers.dartify()));
      expect(response.body.dartify(), equals(expectedResponse.body.dartify()));
    });

  });
}
