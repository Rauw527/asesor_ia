import 'package:flutter/foundation.dart';

/// Static configuration resolved at build time.
///
/// Override with:
///   flutter run --dart-define=API_BASE_URL=http://192.168.1.20:8000
///
/// Without an override the host is picked per platform: the Android emulator
/// reaches the host machine through 10.0.2.2, while browsers and desktop apps
/// talk to localhost. A physical Android device needs the LAN IP of the
/// machine running the API, passed through `--dart-define`.
class AppConfig {
  const AppConfig._();

  static const String _override = String.fromEnvironment('API_BASE_URL');

  static String? serverOverride;

  static String get apiBaseUrl {
    if (serverOverride != null) return serverOverride!;
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8000';
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  static const String apiPrefix = '/api/v1';

  /// Gemini vision calls can take several seconds; keep the client patient.
  static const Duration requestTimeout = Duration(seconds: 90);

  static Uri endpoint(String path, [Map<String, String>? query]) {
    final uri = Uri.parse('$apiBaseUrl$apiPrefix$path');
    if (query == null || query.isEmpty) return uri;
    return uri.replace(queryParameters: query);
  }

  static Uri mediaUrl(String relativeOrAbsolute) {
    if (relativeOrAbsolute.startsWith('http')) {
      return Uri.parse(relativeOrAbsolute);
    }
    return Uri.parse('$apiBaseUrl$relativeOrAbsolute');
  }
}
