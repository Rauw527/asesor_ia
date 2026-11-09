import 'dart:io';

import 'package:flutter/foundation.dart';

import '../models/skin_progress.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';
import '../services/photo_store.dart';

/// Owns the Day-1 baseline photo and the month-over-month comparison.
class ProgressController extends ChangeNotifier {
  ProgressController(this._api, this._store);

  final AsesorApi _api;
  final PhotoStore _store;

  Uint8List? _baselineBytes;
  DateTime? _baselineDate;
  Uint8List? _currentBytes;
  SkinProgress? _result;
  bool _loading = false;
  bool _comparing = false;
  String? _error;

  Uint8List? get baselineBytes => _baselineBytes;
  DateTime? get baselineDate => _baselineDate;
  Uint8List? get currentBytes => _currentBytes;
  SkinProgress? get result => _result;
  bool get loading => _loading;
  bool get comparing => _comparing;
  String? get error => _error;
  bool get hasBaseline => _baselineBytes != null;

  int? get daysSinceBaseline {
    final date = _baselineDate;
    if (date == null) return null;
    return DateTime.now().difference(date).inDays;
  }

  Future<void> loadBaseline() async {
    _loading = true;
    notifyListeners();
    try {
      final file = await _store.baselineFile();
      _baselineDate = await _store.baselineDate();
      _baselineBytes = file == null ? null : await _readFile(file);
    } catch (_) {
      _error = 'No se pudo leer la foto de referencia guardada.';
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  /// Persists a new Day-1 reference and clears any previous comparison so the
  /// slider never mixes photos from two different baselines.
  Future<bool> setBaseline(Uint8List bytes) async {
    try {
      await _store.saveBaseline(bytes);
      _baselineBytes = bytes;
      _baselineDate = DateTime.now();
      _currentBytes = null;
      _result = null;
      _error = null;
      return true;
    } catch (_) {
      _error = 'No se pudo guardar la foto en este dispositivo.';
      return false;
    } finally {
      notifyListeners();
    }
  }

  Future<SkinProgress?> compare(Uint8List currentBytes) async {
    final baseline = _baselineBytes;
    if (baseline == null || _comparing) return null;

    _comparing = true;
    _error = null;
    notifyListeners();

    try {
      final progress = await _api.compareProgress(
        baseline: baseline,
        current: currentBytes,
        daysElapsed: daysSinceBaseline,
      );
      _currentBytes = currentBytes;
      _result = progress;
      return progress;
    } on ApiException catch (error) {
      _error = error.message;
      return null;
    } catch (_) {
      _error = 'No pudimos comparar las fotos. Inténtalo de nuevo.';
      return null;
    } finally {
      _comparing = false;
      notifyListeners();
    }
  }

  Future<void> resetBaseline() async {
    try {
      await _store.clear();
    } catch (_) {
      _error = 'No se pudo borrar la foto de referencia.';
      return;
    }
    _baselineBytes = null;
    _baselineDate = null;
    _currentBytes = null;
    _result = null;
    _error = null;
    notifyListeners();
  }

  Future<Uint8List> _readFile(File file) => file.readAsBytes();
}
