/// Response of `POST /api/v1/skin/analyze`.
class SkinAnalysis {
  const SkinAnalysis({
    required this.skinType,
    required this.hydrationLevel,
    required this.undertone,
    required this.detectedIssues,
    required this.recommendations,
    required this.productSuggestions,
    required this.disclaimer,
  });

  final String skinType;
  final int hydrationLevel;
  final String undertone;
  final List<String> detectedIssues;
  final List<String> recommendations;
  final List<ProductSuggestion> productSuggestions;
  final String disclaimer;

  factory SkinAnalysis.fromJson(Map<String, dynamic> json) {
    return SkinAnalysis(
      skinType: json['skin_type'] as String? ?? 'Sin dato',
      hydrationLevel: (json['hydration_level'] as num?)?.round() ?? 0,
      undertone: json['undertone'] as String? ?? 'Neutro',
      detectedIssues: _stringList(json['detected_issues']),
      recommendations: _stringList(json['recommendations']),
      productSuggestions: (json['product_suggestions'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(ProductSuggestion.fromJson)
          .toList(growable: false),
      disclaimer: json['disclaimer'] as String? ?? '',
    );
  }
}

class ProductSuggestion {
  const ProductSuggestion({
    required this.name,
    required this.brand,
    required this.reason,
    required this.affiliateLink,
  });

  final String name;
  final String brand;
  final String reason;
  final String affiliateLink;

  factory ProductSuggestion.fromJson(Map<String, dynamic> json) {
    return ProductSuggestion(
      name: json['name'] as String? ?? '',
      brand: json['brand'] as String? ?? '',
      reason: json['reason'] as String? ?? '',
      affiliateLink: json['affiliate_link'] as String? ?? '',
    );
  }
}

List<String> _stringList(Object? value) {
  if (value is List) {
    return value.whereType<String>().toList(growable: false);
  }
  return const <String>[];
}
