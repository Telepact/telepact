import 'dart:convert';
import 'dart:html';
import 'dart:js_interop';

import 'package:node_interop/util.dart';
import 'package:test/test.dart';
import 'package:uapi/uapi.dart';
import 'dart:typed_data';

Future<void> loadJavaScript(String src) {
  final script = ScriptElement()
    ..type = 'application/javascript'
    ..src = src;
  document.body?.append(script);
  return script.onLoad.first;
}

void main() {
  group('Server', () {
    setUpAll(() async {
      await loadJavaScript('index.cjs.js');
    });

    test('should process request message bytes', () async {
      final uapiPseudoJson = [
        {
          "struct.Data": {
            "field": ["boolean"]
          }
        }
      ];
      final uapiJson = jsonEncode(uapiPseudoJson);
      final uapiSchema = UApiSchema.fromJson(uapiJson);
      if (uapiSchema == null) {
        fail('uapiSchema is null');
      }

      final handler = (Message requestMessage) async {
        return Message(JSObject(), JSObject());
      };

      final serverOptions = ServerOptions()..authRequired = false;
      final server = Server(uapiSchema, handler, serverOptions);
      if (server == null) {
        fail('server is null');
      }

      final requestMessageBytes = Uint8List.fromList([1, 2, 3]);
      dynamic request = [
        {},
        {"ping_": {}}
      ];
      dynamic requestBytes = jsonEncode(request);
      final responseBytes = await server.process(requestBytes);
      if (responseBytes == null) {
        fail('responseBytes is null');
      }
      dynamic response = jsonDecode(utf8.decode(responseBytes));
      dynamic expectedResponse = [
        {},
        {"Ok_": {}}
      ];
      expect(response, equals(expectedResponse));
    });
  });
}
