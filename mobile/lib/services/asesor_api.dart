import 'dart:typed_data';

import '../models/inci_scan.dart';
import '../models/routine.dart';
import '../models/skin_analysis.dart';
import '../models/skin_progress.dart';
import '../models/user_profile.dart';
import 'api_client.dart';

/// Typed facade over the Phase 1 endpoints.
class AsesorApi {
  AsesorApi({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  String? get token => _client.token;
  Map<String, String> get authHeaders => _client.authHeaders;
  set onUnauthorized(void Function()? callback) =>
      _client.onUnauthorized = callback;

  Future<void> login(String email, String password) async {
    final response = await _client.postJson('/auth/login', {
      'email': email,
      'password': password,
    });
    _client.token = response['access_token'] as String;
  }

  Future<void> register(String name, String email, String password) async {
    await _client.postJson('/auth/register', {
      'full_name': name,
      'email': email,
      'password': password,
    });
  }

  void logout() => _client.token = null;
  Future<List<dynamic>> consents() => _client.getList('/consents');
  Future<void> saveConsent(String type, bool granted) async {
    await _client.postJson('/consents', {
      'consent_type': type,
      'granted': granted,
      'version': 'android-demo-1',
      'purpose': type == 'service'
          ? 'Guardar fotos privadas para la demo, hasta que las elimines. Sin envío a IA externa.'
          : 'Participación opcional en un futuro dataset. No se entrena ningún modelo en esta demo.',
    });
  }

  Future<Map<String, dynamic>?> questionnaire() =>
      _client.getNullable('/questionnaires/latest');
  Future<void> saveQuestionnaire(Map<String, String> answers) async {
    await _client.postJson('/questionnaires', {
      'answers': answers.entries
          .map(
            (e) => {
              'question_key': e.key,
              'answer_value': e.value,
              'answer_type': 'single',
            },
          )
          .toList(),
    });
  }

  Future<Map<String, dynamic>> buildProfile() =>
      _client.postJson('/skin-profile/build', {});
  Future<Map<String, dynamic>> recommend(String type) =>
      _client.postJson('/recommendations?routine_type=$type', {});
  Future<List<dynamic>> photos() => _client.getList('/photos');
  Future<List<dynamic>> analyses() => _client.getList('/analysis/history');
  Future<String> uploadPhoto(String type, Uint8List bytes) async {
    final response = await _client.postMultipart(
      '/photos',
      fields: {'photo_type': type},
      files: {'file': UploadFile(bytes: bytes, filename: '$type.jpg')},
    );
    return response['photo_id'] as String;
  }

  Future<void> deletePhoto(String id) => _client.delete('/photos/$id');
  Future<Map<String, dynamic>> demoAnalysis(List<String> ids) =>
      _client.postJson('/analysis', {'photo_ids': ids});

  Future<UserProfile> me() async {
    final json = await _client.get('/users/me');
    return UserProfile.fromJson(json);
  }

  Future<SkinAnalysis> analyzeSkin(Uint8List image) async {
    final json = await _client.postMultipart(
      '/skin/analyze',
      files: {'file': UploadFile(bytes: image, filename: 'selfie.jpg')},
    );
    return SkinAnalysis.fromJson(json);
  }

  Future<SkinProgress> compareProgress({
    required Uint8List baseline,
    required Uint8List current,
    int? daysElapsed,
  }) async {
    final fields = <String, String>{};
    if (daysElapsed != null) fields['days_elapsed'] = '$daysElapsed';

    final json = await _client.postMultipart(
      '/skin/compare-progress',
      fields: fields,
      files: {
        'baseline_file': UploadFile(bytes: baseline, filename: 'baseline.jpg'),
        'current_file': UploadFile(bytes: current, filename: 'current.jpg'),
      },
    );
    return SkinProgress.fromJson(json);
  }

  Future<InciScan> scanInci(Uint8List image) async {
    final json = await _client.postMultipart(
      '/inci/scan',
      files: {'file': UploadFile(bytes: image, filename: 'label.jpg')},
    );
    return InciScan.fromJson(json);
  }

  Future<RoutineDay> routineToday({DateTime? date}) async {
    final target = date ?? DateTime.now();
    final json = await _client.get(
      '/routine/today',
      query: {'date': _formatDate(target)},
    );
    return RoutineDay.fromJson(json);
  }

  Future<RoutineLog> checkin({
    required String period,
    required List<String> completedSteps,
    String notes = '',
  }) async {
    final json = await _client.postJson('/routine/checkin', {
      'period': period,
      'log_date': _formatDate(DateTime.now()),
      'completed_steps': completedSteps,
      'notes': notes,
    });
    final log = json['log'];
    if (log is! Map<String, dynamic>) {
      throw ApiException(
        'Respuesta inesperada del servidor al guardar la rutina.',
      );
    }
    return RoutineLog.fromJson(log);
  }

  Future<void> addProductToRoutine({
    required String name,
    required List<String> keyIngredients,
  }) async {
    await _client.postJson('/products', {
      'name': name,
      'key_ingredients': keyIngredients,
      'is_active': true,
    });
  }

  static String _formatDate(DateTime date) {
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    return '${date.year}-$month-$day';
  }
}
