import 'package:asesor_ia/main.dart';
import 'package:asesor_ia/models/routine.dart';
import 'package:asesor_ia/models/user_profile.dart';
import 'package:asesor_ia/services/asesor_api.dart';
import 'package:asesor_ia/theme/app_theme.dart';
import 'package:asesor_ia/widgets/metric_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Avoids network calls while still exercising the real controllers.
class _FakeApi extends AsesorApi {
  @override
  Future<UserProfile> me() async {
    return const UserProfile(
      id: 'demo',
      email: 'demo@asesor.ia',
      fullName: 'Ana Torres',
      onboardingCompleted: true,
      skinProfile: SkinProfile(
        skinType: 'Mixta',
        hydrationLevel: 62,
        undertone: 'Cálido',
        detectedIssues: ['Poros dilatados'],
        recommendations: ['Limpiador suave'],
      ),
    );
  }

  @override
  Future<RoutineDay> routineToday({DateTime? date}) async {
    return RoutineDay(
      date: date ?? DateTime.now(),
      allowedSteps: const {
        'AM': ['limpiador', 'vitamina_c', 'hidratante', 'protector_solar'],
        'PM': ['limpiador', 'tratamiento', 'hidratante'],
      },
      streakDays: 3,
    );
  }

  @override
  Future<RoutineLog> checkin({
    required String period,
    required List<String> completedSteps,
    String notes = '',
  }) async {
    return RoutineLog(
      period: period,
      completedSteps: completedSteps,
      notes: notes,
      completed: false,
    );
  }
}

void main() {
  testWidgets('home renders the profile summary and routine', (tester) async {
    await tester.pumpWidget(AsesorIaApp(api: _FakeApi()));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Hola, Ana'), findsOneWidget);
    expect(find.text('Tu piel'), findsOneWidget);
    expect(find.text('Mixta'), findsOneWidget);
    expect(find.text('Cálido'), findsOneWidget);
    expect(find.text('Rutina de hoy'), findsOneWidget);
    expect(find.text('3 días'), findsOneWidget);
    expect(find.text('Limpiador'), findsNWidgets(2));
  });

  testWidgets('checking a step keeps the local state', (tester) async {
    await tester.pumpWidget(AsesorIaApp(api: _FakeApi()));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    final checkbox = find.byType(Checkbox).first;
    expect(checkbox, findsOneWidget);

    await tester.tap(checkbox);
    await tester.pump();

    final updated = tester.widget<Checkbox>(checkbox);
    expect(updated.value, isTrue);
  });

  testWidgets('MetricCard renders its value and progress bar', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.light(),
        home: const Scaffold(
          body: MetricCard(
            label: 'Progreso',
            value: '42%',
            progress: 0.42,
          ),
        ),
      ),
    );

    expect(find.text('Progreso'), findsOneWidget);
    expect(find.text('42%'), findsOneWidget);
    expect(find.byType(LinearProgressIndicator), findsOneWidget);
  });
}
