import 'package:flutter/foundation.dart';

import '../models/inci_scan.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';

/// Scans an INCI label and lets the user register the product in their routine.
class InciController extends ChangeNotifier {
  InciController(this._api);

  final AsesorApi _api;

  InciScan? _scan;
  Uint8List? _labelImage;
  bool _scanning = false;
  bool _saving = false;
  bool _saved = false;
  String? _error;

  InciScan? get scan => _scan;
  Uint8List? get labelImage => _labelImage;
  bool get scanning => _scanning;
  bool get saving => _saving;
  bool get saved => _saved;
  String? get error => _error;

  Future<InciScan?> scanLabel(Uint8List imageBytes) async {
    if (_scanning) return null;

    _scanning = true;
    _error = null;
    _saved = false;
    notifyListeners();

    try {
      final result = await _api.scanInci(imageBytes);
      _scan = result;
      _labelImage = imageBytes;
      return result;
    } on ApiException catch (error) {
      _error = error.message;
      return null;
    } catch (_) {
      _error = 'No pudimos leer la etiqueta. Intenta con más luz y de frente.';
      return null;
    } finally {
      _scanning = false;
      notifyListeners();
    }
  }

  /// Registers the scanned product as part of the active routine so later scans
  /// can flag real conflicts against it.
  Future<bool> addToRoutine() async {
    final result = _scan;
    if (result == null || result.keyIngredients.isEmpty || _saving) {
      return false;
    }

    _saving = true;
    _error = null;
    notifyListeners();

    try {
      await _api.addProductToRoutine(
        name: result.productName,
        keyIngredients: result.keyIngredients,
      );
      _saved = true;
      return true;
    } on ApiException catch (error) {
      _error = error.message;
      return false;
    } catch (_) {
      _error = 'No se pudo guardar el producto en tu rutina.';
      return false;
    } finally {
      _saving = false;
      notifyListeners();
    }
  }

  void reset() {
    _scan = null;
    _labelImage = null;
    _error = null;
    _saved = false;
    notifyListeners();
  }
}
