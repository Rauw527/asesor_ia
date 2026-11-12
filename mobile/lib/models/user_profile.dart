/// Demo user profile (`GET /api/v1/users/me`).
class UserProfile {
  const UserProfile({
    required this.id,
    required this.email,
    required this.fullName,
    required this.onboardingCompleted,
    this.skinProfile,
  });

  final String id;
  final String email;
  final String fullName;
  final bool onboardingCompleted;
  final SkinProfile? skinProfile;

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    final profile = json['skin_profile'];
    return UserProfile(
      id: json['id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      skinProfile: profile is Map<String, dynamic>
          ? SkinProfile.fromJson(profile)
          : null,
    );
  }

  String get displayName {
    final trimmed = fullName.trim();
    if (trimmed.isEmpty) return 'Bienvenida';
    return trimmed.split(' ').first;
  }
}

/// Cosmetic profile. Phase 2 slots (`colorimetrySeason`, `bodyShape`,
/// `stylePreference`) already exist server-side and are surfaced here so the
/// outfit module can reuse this model unchanged.
class SkinProfile {
  const SkinProfile({
    this.skinType,
    this.hydrationLevel,
    this.undertone,
    this.detectedIssues = const [],
    this.recommendations = const [],
    this.colorimetrySeason,
    this.bodyShape,
    this.stylePreference,
  });

  final String? skinType;
  final int? hydrationLevel;
  final String? undertone;
  final List<String> detectedIssues;
  final List<String> recommendations;
  final String? colorimetrySeason;
  final String? bodyShape;
  final String? stylePreference;

  factory SkinProfile.fromJson(Map<String, dynamic> json) {
    return SkinProfile(
      skinType: json['skin_type'] as String?,
      hydrationLevel: (json['hydration_level'] as num?)?.round(),
      undertone: json['undertone'] as String?,
      detectedIssues: (json['detected_issues'] as List<dynamic>? ?? [])
          .whereType<String>()
          .toList(),
      recommendations: (json['recommendations'] as List<dynamic>? ?? [])
          .whereType<String>()
          .toList(),
      colorimetrySeason: json['colorimetry_season'] as String?,
      bodyShape: json['body_shape'] as String?,
      stylePreference: json['style_preference'] as String?,
    );
  }
}
