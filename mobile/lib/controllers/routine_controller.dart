import 'package:flutter/foundation.dart';

import '../models/routine.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';

/// Keeps the AM/PM checklist in sync with `POST /api/v1/routine/checkin`.
///
/// Toggles are optimistic: the checkbox flips immediately and the server call
/// is serialized per period so fast taps can never overwrite each other.
class RoutineController extends ChangeNotifier {
  RoutineController(this._api);

  final AsesorApi _api;

  static const Map<String, List<String>> fallbackSteps = {
    'AM': ['limpiador', 'vitamina_c', 'hidratante', 'protector_solar'],
    'PM': ['limpiador', 'tratamiento', 'hidratante'],
  };

  RoutineDay? _day;
  bool _loading = false;
  String? _error;
  int _streakDays = 0;

  final Map<String, Set<String>> _steps = {
    'AM': <String>{},
    'PM': <String>{},
  };
  final Map<String, Set<String>> _confirmed = {
    'AM': <String>{},
    'PM': <String>{},
  };
  final Set<String> _saving = <String>{};
  final Map<String, Future<void>> _queues = <String, Future<void>>{};

  RoutineDay? get day => _day;
  bool get loading => _loading;
  String? get error => _error;
  int get streakDays => _streakDays;

  List<String> stepsFor(String period) =>
      _day?.allowedSteps[period] ?? fallbackSteps[period] ?? const <String>[];

  Set<String> completedFor(String period) =>
      _steps[period] ?? const <String>{};

  bool savingPeriod(String period) => _saving.contains(period);

  bool isPeriodComplete(String period) {
    final steps = stepsFor(period);
    if (steps.isEmpty) return false;
    return steps.every(completedFor(period).contains);
  }

  double progressFor(String period) {
    final steps = stepsFor(period);
    if (steps.isEmpty) return 0;
    return completedFor(period).where(steps.contains).length / steps.length;
  }

  Future<void> load() async {
    if (_loading) return;
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final day = await _api.routineToday();
      _day = day;
      _streakDays = day.streakDays;
      for (final period in const ['AM', 'PM']) {
        final completed = Set<String>.from(
          day.logFor(period)?.completedSteps ?? const <String>[],
        );
        _steps[period] = completed;
        _confirmed[period] = Set<String>.from(completed);
      }
    } on ApiException catch (error) {
      _error = error.message;
    } catch (_) {
      _error = 'No se pudo cargar tu rutina. Revisa la conexión.';
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  void toggle(String period, String step) {
    final current = _steps[period];
    if (current == null) return;

    if (!current.add(step)) {
      current.remove(step);
    }
    _error = null;
    notifyListeners();
    _enqueue(period);
  }

  void clearError() {
    if (_error == null) return;
    _error = null;
    notifyListeners();
  }

  void _enqueue(String period) {
    final previous = _queues[period] ?? Future<void>.value();
    _queues[period] = previous.then((_) => _push(period));
  }

  Future<void> _push(String period) async {
    final target = Set<String>.from(_steps[period] ?? const <String>{});

    _saving.add(period);
    notifyListeners();

    try {
      final log = await _api.checkin(
        period: period,
        completedSteps: target.toList(),
      );
      _confirmed[period] = Set<String>.from(log.completedSteps);

      // Only adopt the server copy when the user has not toggled again while
      // the request was in flight.
      if (setEquals(_steps[period], target)) {
        _steps[period] = Set<String>.from(log.completedSteps);
      }
      if (isPeriodComplete(period)) {
        await _refreshStreak();
      }
    } on ApiException catch (error) {
      _error = error.message;
      _steps[period] = Set<String>.from(_confirmed[period] ?? const <String>{});
    } catch (_) {
      _error = 'No se pudo guardar el checklist. Inténtalo de nuevo.';
      _steps[period] = Set<String>.from(_confirmed[period] ?? const <String>{});
    } finally {
      _saving.remove(period);
      notifyListeners();
    }
  }

  Future<void> _refreshStreak() async {
    try {
      final day = await _api.routineToday();
      _streakDays = day.streakDays;
    } on ApiException {
      // Streak is decorative; a failure must not break the checklist.
    }
  }
}
