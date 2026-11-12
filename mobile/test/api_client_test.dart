import 'dart:typed_data';
import 'package:asesor_ia/services/api_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test(
    'sends the session on reads, lists, uploads, writes and deletion',
    () async {
      final requests = <http.Request>[];
      final client = ApiClient(
        client: MockClient((request) async {
          requests.add(request);
          if (request.method == 'DELETE') return http.Response('', 204);
          if (request.url.path.endsWith('/list')) {
            return http.Response('[]', 200);
          }
          return http.Response('{}', 200);
        }),
      )..token = 'private-test-token';
      await client.get('/read');
      await client.getList('/list');
      await client.postJson('/write', {});
      await client.postMultipart(
        '/upload',
        files: {
          'file': UploadFile(
            bytes: Uint8List.fromList([1, 2]),
            filename: 'x.jpg',
          ),
        },
      );
      await client.delete('/delete');
      expect(requests.length, 5);
      expect(
        requests.every(
          (r) => r.headers['Authorization'] == 'Bearer private-test-token',
        ),
        isTrue,
      );
    },
  );
  test(
    'an expired session is cleared and reports authentication failure',
    () async {
      var expired = false;
      final client =
          ApiClient(
              client: MockClient(
                (_) async => http.Response('{"detail":"No autenticado"}', 401),
              ),
            )
            ..token = 'expired'
            ..onUnauthorized = () {
              expired = true;
            };
      await expectLater(
        client.get('/private'),
        throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 401)),
      );
      expect(client.token, isNull);
      expect(expired, isTrue);
    },
  );
  test('nullable questionnaire can be absent for a new account', () async {
    final client = ApiClient(
      client: MockClient((_) async => http.Response('null', 200)),
    );
    expect(await client.getNullable('/questionnaires/latest'), isNull);
  });
}
