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
      throw ApiException('Respuesta inesperada del servidor al guardar la rutina.');
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
