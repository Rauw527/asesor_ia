/// Response of `POST /api/v1/inci/scan`.
class InciScan {
  const InciScan({
    required this.productName,
    required this.keyIngredients,
    required this.hasConflict,
    this.conflictWarning,
    this.safeAlternative,
  });

  final String productName;
  final List<String> keyIngredients;
  final bool hasConflict;
  final String? conflictWarning;
  final SafeAlternative? safeAlternative;

  factory InciScan.fromJson(Map<String, dynamic> json) {
    final alternative = json['safe_alternative'];
    return InciScan(
      productName: json['product_name'] as String? ?? 'Producto sin identificar',
      keyIngredients: (json['key_ingredients'] as List<dynamic>? ?? [])
          .whereType<String>()
          .toList(growable: false),
      hasConflict: json['has_conflict'] as bool? ?? false,
      conflictWarning: json['conflict_warning'] as String?,
      safeAlternative: alternative is Map<String, dynamic>
          ? SafeAlternative.fromJson(alternative)
          : null,
    );
  }
}

class SafeAlternative {
  const SafeAlternative({
    required this.name,
    required this.reason,
    required this.affiliateLink,
  });

  final String name;
  final String reason;
  final String affiliateLink;

  factory SafeAlternative.fromJson(Map<String, dynamic> json) {
    return SafeAlternative(
      name: json['name'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
      affiliateLink: json['affiliate_link'] as String? ?? '',
    );
  }
}
