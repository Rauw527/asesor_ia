/// Response of `POST /api/v1/skin/compare-progress`.
class SkinProgress {
  const SkinProgress({
    required this.progressPercentage,
    required this.hydrationChange,
    required this.textureImprovement,
    required this.summaryNotes,
    required this.recommendedRoutineAdjustments,
  });

  final int progressPercentage;
  final String hydrationChange;
  final String textureImprovement;
  final String summaryNotes;
  final List<String> recommendedRoutineAdjustments;

  factory SkinProgress.fromJson(Map<String, dynamic> json) {
    return SkinProgress(
      progressPercentage: (json['progress_percentage'] as num?)?.round() ?? 0,
      hydrationChange: json['hydration_change'] as String? ?? '',
      textureImprovement: json['texture_improvement'] as String? ?? '',
      summaryNotes: json['summary_notes'] as String? ?? '',
      recommendedRoutineAdjustments:
          (json['recommended_routine_adjustments'] as List<dynamic>? ?? [])
              .whereType<String>()
              .toList(growable: false),
    );
  }
}
