/// Daily routine contracts (`/api/v1/routine/*`).
class RoutineLog {
  const RoutineLog({
    required this.period,
    required this.completedSteps,
    required this.notes,
    required this.completed,
  });

  final String period;
  final List<String> completedSteps;
  final String notes;
  final bool completed;

  factory RoutineLog.fromJson(Map<String, dynamic> json) {
    return RoutineLog(
      period: json['period'] as String? ?? '',
      completedSteps: (json['completed_steps'] as List<dynamic>? ?? [])
          .whereType<String>()
          .toList(growable: false),
      notes: json['notes'] as String? ?? '',
      completed: json['completed'] as bool? ?? false,
    );
  }
}

class RoutineDay {
  const RoutineDay({
    required this.date,
    required this.allowedSteps,
    required this.streakDays,
    this.am,
    this.pm,
  });

  final DateTime date;
  final Map<String, List<String>> allowedSteps;
  final int streakDays;
  final RoutineLog? am;
  final RoutineLog? pm;

  factory RoutineDay.fromJson(Map<String, dynamic> json) {
    final steps = <String, List<String>>{};
    final rawSteps = json['allowed_steps'];
    if (rawSteps is Map<String, dynamic>) {
      rawSteps.forEach((key, value) {
        steps[key] = (value as List<dynamic>? ?? []).whereType<String>().toList(
          growable: false,
        );
      });
    }

    final rawAm = json['am'];
    final rawPm = json['pm'];

    return RoutineDay(
      date:
          DateTime.tryParse(json['log_date'] as String? ?? '') ??
          DateTime.now(),
      allowedSteps: steps,
      streakDays: (json['streak_days'] as num?)?.round() ?? 0,
      am: rawAm is Map<String, dynamic> ? RoutineLog.fromJson(rawAm) : null,
      pm: rawPm is Map<String, dynamic> ? RoutineLog.fromJson(rawPm) : null,
    );
  }

  RoutineLog? logFor(String period) => period == 'AM' ? am : pm;
}

/// Human labels for the canonical step slugs the API validates against.
const Map<String, String> routineStepLabels = {
  'limpiador': 'Limpiador',
  'vitamina_c': 'Vitamina C',
  'hidratante': 'Hidratante',
  'protector_solar': 'Protector solar',
  'tratamiento': 'Tratamiento',
};
