import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

/// Error surfaced to the UI with a message that is safe to show to a user.
class ApiException implements Exception {
  ApiException(this.message, {this.statusCode, this.code});

  final String message;
  final int? statusCode;
  final String? code;

  bool get isOffline => statusCode == null;

  @override
  String toString() => message;
}

class UploadFile {
  const UploadFile({required this.bytes, required this.filename});

  final Uint8List bytes;
  final String filename;
}

/// Thin HTTP layer: builds multipart bodies, decodes JSON and normalizes errors.
class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? query,
  }) async {
    final response = await _guard(
      () => _client.get(AppConfig.endpoint(path, query)),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, Object?> body,
  ) async {
    final response = await _guard(
      () => _client.post(
        AppConfig.endpoint(path),
        headers: const {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      ),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> postMultipart(
    String path, {
    Map<String, String> fields = const {},
    required Map<String, UploadFile> files,
  }) async {
    final response = await _guard(() async {
      final request = http.MultipartRequest('POST', AppConfig.endpoint(path));
      request.fields.addAll(fields);
      for (final entry in files.entries) {
        request.files.add(
          http.MultipartFile.fromBytes(
            entry.key,
            entry.value.bytes,
            filename: entry.value.filename,
          ),
        );
      }
      final streamed = await _client.send(request);
      return http.Response.fromStream(streamed);
    });
    return _decode(response);
  }

  Future<http.Response> _guard(Future<http.Response> Function() action) async {
    try {
      return await action().timeout(AppConfig.requestTimeout);
    } on TimeoutException {
      throw ApiException(
        'El servidor tardó demasiado en responder. Revisa tu conexión e '
        'inténtalo de nuevo.',
      );
    } on http.ClientException catch (error) {
      throw ApiException(
        'No se pudo conectar con el servidor en ${AppConfig.apiBaseUrl} '
        '(${error.message}). Verifica que la API esté corriendo y que la URL '
        'sea accesible desde este dispositivo.',
      );
    } catch (error) {
      throw ApiException('Error de red inesperado: $error');
    }
  }

  Map<String, dynamic> _decode(http.Response response) {
    final body = _tryDecode(response.body);

    if (response.statusCode >= 400) {
      throw ApiException(
        _extractDetail(body) ?? 'Error ${response.statusCode} del servidor.',
        statusCode: response.statusCode,
        code: body?['code'] as String?,
      );
    }

    if (body == null) {
      throw ApiException(
        'El servidor devolvió una respuesta ilegible.',
        statusCode: response.statusCode,
      );
    }
    return body;
  }

  Map<String, dynamic>? _tryDecode(String raw) {
    if (raw.isEmpty) return null;
    try {
      final decoded = jsonDecode(raw);
      return decoded is Map<String, dynamic> ? decoded : null;
    } catch (_) {
      return null;
    }
  }

  String? _extractDetail(Map<String, dynamic>? body) {
    if (body == null) return null;
    final detail = body['detail'];
    if (detail is String) return detail;
    if (detail is List && detail.isNotEmpty) {
      final first = detail.first;
      if (first is Map && first['msg'] is String) return first['msg'] as String;
    }
    return null;
  }
}
