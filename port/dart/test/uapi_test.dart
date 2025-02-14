import 'dart:convert';
import 'dart:html';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:node_interop/util.dart';
import 'package:test/test.dart';
import 'package:uapi/uapi.dart';
import 'dart:typed_data';

extension type Window(JSObject _) implements JSObject {}

void main() {
  group('Server', () {
    test('should process request message bytes', () async {
      print('Test started');

      // Print all files loaded in the browser
      print('Loaded scripts:');
      print(window.document.getElementsByTagName('script'));

      // Print the names of the javascript files loaded in the browser
      print('Script sources:');
      print(window.document
          .getElementsByTagName('script')
          .map((e) => (e as ScriptElement).src));

      // Print the first 10 lines of each script file
      for (var scriptElement
          in window.document.getElementsByTagName('script')) {
        final src = (scriptElement as ScriptElement).src;
        if (src.isNotEmpty) {
          print('Checking contents of $src');
          final scriptContent = await HttpRequest.getString(src);
          final lines = scriptContent.split('\n');
          print('First 10 lines of $src:');
          for (var i = 0; i < 10 && i < lines.length; i++) {
            print(lines[i]);
          }
        }
      }

      // Print the contents of window.UApi
      print('Contents of window.UApi:');
      print((window as Window).getProperty('UApi'.toJS));
      print(globalContext.getProperty("UApi".toJS));

      final uapiPseudoJson = [
        {
          "struct.Data": {
            "field": ["boolean"]
          }
        }
      ];
      print("Encoding json");
      final uapiJson = jsonEncode(uapiPseudoJson);
      print('Creating UApiSchema');
      final uapiSchema = UApiSchema.fromJson(uapiJson);
      print('UApiSchema created: $uapiSchema');

      JSPromise handler(Message requestMessage) {
        print('Handler called with requestMessage: $requestMessage');
        return Future.value(Message(JSObject(), JSObject())).toJS;
      }

      print('Creating ServerOptions');
      final serverOptions = ServerOptions()..authRequired = false;
      print('ServerOptions created: $serverOptions');

      print('Creating Server');
      final server = Server(uapiSchema, handler.toJS, serverOptions);
      print('Server created: $server');

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      print('Request message bytes: $requestMessageBytes');

      dynamic request = [
        {},
        {"ping_": {}}
      ];
      dynamic requestBytes = jsonEncode(request);
      print('Request bytes: $requestBytes');

      print('Processing request');
      final responseBytes = await server.process(requestBytes).toDart;
      print('Response bytes: $responseBytes');
      if (responseBytes == null) {
        fail('responseBytes is null');
      }

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
