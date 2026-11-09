
import 'package:flutter/foundation.dart';

import '../models/skin_analysis.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';

/// Runs the facial diagnosis and keeps the latest result in memory.
class SkinController extends ChangeNotifier {
  SkinController(this._api);

  final AsesorApi _api;

  SkinAnalysis? _analysis;
  Uint8List? _lastImage;
  bool _analyzing = false;
  String? _error;

  SkinAnalysis? get analysis => _analysis;
  Uint8List? get lastImage => _lastImage;
  bool get analyzing => _analyzing;
  String? get error => _error;

  Future<SkinAnalysis?> analyze(Uint8List imageBytes) async {
    if (_analyzing) return null;

    _analyzing = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _api.analyzeSkin(imageBytes);
      _analysis = result;
      _lastImage = imageBytes;
      return result;
    } on ApiException catch (error) {
      _error = error.message;
      return null;
    } catch (_) {
      _error = 'No pudimos procesar la imagen. Intenta con otra foto.';
      return null;
    } finally {
      _analyzing = false;
      notifyListeners();
    }
  }

  void clearError() {
    if (_error == null) return;
    _error = null;
    notifyListeners();
  }
}
