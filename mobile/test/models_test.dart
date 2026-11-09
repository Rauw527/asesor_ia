import 'package:asesor_ia/models/inci_scan.dart';
import 'package:asesor_ia/models/routine.dart';
import 'package:asesor_ia/models/skin_analysis.dart';
import 'package:asesor_ia/models/skin_progress.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('SkinAnalysis parses the exact API contract', () {
    final analysis = SkinAnalysis.fromJson({
      'skin_type': 'Mixta',
      'hydration_level': 64,
      'undertone': 'Cálido',
      'detected_issues': ['Poros dilatados', 'Líneas finas'],
      'recommendations': ['Limpiador suave'],
      'product_suggestions': [
        {
          'name': 'Hidratante ligero',
          'brand': 'Marca',
          'reason': 'Textura no comedogénica',
          'affiliate_link': 'https://example.com/p/1',
        },
      ],
      'disclaimer': 'No sustituye una consulta dermatológica.',
    });

    expect(analysis.skinType, 'Mixta');
    expect(analysis.hydrationLevel, 64);
    expect(analysis.undertone, 'Cálido');
    expect(analysis.detectedIssues, hasLength(2));
    expect(analysis.productSuggestions.single.brand, 'Marca');
    expect(analysis.productSuggestions.single.affiliateLink, isNotEmpty);
  });

  test('SkinProgress parses numeric and text fields', () {
    final progress = SkinProgress.fromJson({
      'progress_percentage': 38,
      'hydration_change': '+12% de hidratación',
      'texture_improvement': 'Poros menos visibles',
      'summary_notes': 'Buena evolución general.',
      'recommended_routine_adjustments': ['Añadir niacinamida'],
    });

    expect(progress.progressPercentage, 38);
    expect(progress.hydrationChange, contains('12'));
    expect(progress.recommendedRoutineAdjustments.single, 'Añadir niacinamida');
  });

  test('InciScan parses a safe alternative', () {
    final scan = InciScan.fromJson({
      'product_name': 'Sérum X',
      'key_ingredients': ['Retinol', 'AHA'],
      'has_conflict': true,
      'conflict_warning': 'No combines retinol con AHA.',
      'safe_alternative': {
        'name': 'Sérum suave',
        'reason': 'Sin ácidos irritantes.',
        'affiliate_link': 'https://example.com/p/2',
      },
    });

    expect(scan.hasConflict, isTrue);
    expect(scan.safeAlternative, isNotNull);
    expect(scan.safeAlternative!.name, 'Sérum suave');
  });

  test('RoutineDay reads logs, allowed steps and streak', () {
    final day = RoutineDay.fromJson({
      'log_date': '2026-11-04',
      'am': {
        'id': '1',
        'log_date': '2026-11-04',
        'period': 'AM',
        'completed_steps': ['limpiador'],
        'notes': '',
        'completed': false,
      },
      'pm': null,
      'allowed_steps': {
        'AM': ['limpiador', 'protector_solar'],
        'PM': ['limpiador'],
      },
      'streak_days': 5,
    });

    expect(day.streakDays, 5);
    expect(day.allowedSteps['AM'], hasLength(2));
    expect(day.logFor('AM')!.completedSteps.single, 'limpiador');
    expect(day.logFor('PM'), isNull);
    expect(routineStepLabels['limpiador'], 'Limpiador');
  });
}
