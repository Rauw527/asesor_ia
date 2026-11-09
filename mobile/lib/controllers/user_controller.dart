import 'package:flutter/foundation.dart';

import '../models/user_profile.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';

/// Loads and exposes the demo user plus its cosmetic profile.
class UserController extends ChangeNotifier {
  UserController(this._api);

  final AsesorApi _api;

  UserProfile? _profile;
  bool _loading = false;
  String? _error;

  UserProfile? get profile => _profile;
  bool get loading => _loading;
  String? get error => _error;
  SkinProfile? get skinProfile => _profile?.skinProfile;

  Future<void> load({bool force = false}) async {
    if (_loading) return;
    if (!force && _profile != null) return;

    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _profile = await _api.me();
    } on ApiException catch (error) {
      _error = error.message;
    } catch (_) {
      _error = 'No se pudo cargar tu perfil. Revisa la conexión con el servidor.';
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  /// The backend updates the stored profile after every analysis, so a reload
  /// keeps the home card in sync with what the AI just detected.
  Future<void> refreshAfterAnalysis() => load(force: true);
}
