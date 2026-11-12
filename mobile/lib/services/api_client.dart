import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';

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

/// Tokens live only in memory. Restarting the app requires signing in again.
class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();
  final http.Client _client;
  String? token;
  void Function()? onUnauthorized;
  Map<String, String> get authHeaders => {
    if (token != null) 'Authorization': 'Bearer $token',
  };

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? query,
  }) async => Map<String, dynamic>.from(
    await _request(
          () => _client.get(
            AppConfig.endpoint(path, query),
            headers: authHeaders,
          ),
        )
        as Map,
  );

  Future<Map<String, dynamic>?> getNullable(String path) async {
    final result = await _request(
      () => _client.get(AppConfig.endpoint(path), headers: authHeaders),
    );
    return result == null ? null : Map<String, dynamic>.from(result as Map);
  }

  Future<List<dynamic>> getList(String path) async =>
      await _request(
            () => _client.get(AppConfig.endpoint(path), headers: authHeaders),
          )
          as List<dynamic>;

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, Object?> body,
  ) async => Map<String, dynamic>.from(
    await _request(
          () => _client.post(
            AppConfig.endpoint(path),
            headers: {...authHeaders, 'Content-Type': 'application/json'},
            body: jsonEncode(body),
          ),
        )
        as Map,
  );

  Future<void> delete(String path) async {
    await _request(
      () => _client.delete(AppConfig.endpoint(path), headers: authHeaders),
    );
  }

  Future<Map<String, dynamic>> postMultipart(
    String path, {
    Map<String, String> fields = const {},
    required Map<String, UploadFile> files,
  }) async {
    return Map<String, dynamic>.from(
      await _request(() async {
            final request = http.MultipartRequest(
              'POST',
              AppConfig.endpoint(path),
            );
            request.headers.addAll(authHeaders);
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
            return http.Response.fromStream(await _client.send(request));
          })
          as Map,
    );
  }

  Future<dynamic> _request(Future<http.Response> Function() send) async {
    try {
      final response = await send().timeout(AppConfig.requestTimeout);
      dynamic body;
      try {
        body = response.body.isEmpty ? null : jsonDecode(response.body);
      } catch (_) {
        body = null;
      }
      if (response.statusCode >= 400) {
        if (response.statusCode == 401 && token != null) {
          token = null;
          onUnauthorized?.call();
        }
        final detail = body is Map ? body['detail'] : null;
        throw ApiException(
          detail is String
              ? detail
              : 'No se pudo completar la solicitud (${response.statusCode}).',
          statusCode: response.statusCode,
          code: body is Map ? body['code'] as String? : null,
        );
      }
      if (response.statusCode == 204 || response.body.trim() == "null") {
        return null;
      }
      if (body == null) {
        throw ApiException('El servidor devolvió una respuesta ilegible.');
      }
      return body;
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw ApiException('El servidor tardó demasiado en responder.');
    } on http.ClientException {
      throw ApiException(
        'No se pudo conectar con ${AppConfig.apiBaseUrl}. Comprueba que el servidor esté encendido y sea accesible desde el teléfono.',
      );
    }
  }
}
