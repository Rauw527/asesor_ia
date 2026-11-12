import 'package:asesor_ia/main.dart';
import 'package:asesor_ia/models/routine.dart';
import 'package:asesor_ia/models/user_profile.dart';
import 'package:asesor_ia/services/asesor_api.dart';
import 'package:asesor_ia/views/android_demo.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class FakeApi extends AsesorApi {
  bool signedIn = false;
  Map<String, String>? savedAnswers;
  final Map<String, bool> decisions = {};
  @override
  String? get token => signedIn ? 'test-token' : null;
  @override
  Future<void> login(String email, String password) async {
    signedIn = true;
  }

  @override
  void logout() {
    signedIn = false;
  }

  @override
  Future<UserProfile> me() async => const UserProfile(
    id: 'test',
    email: 'test@example.org',
    fullName: 'Ana Torres',
    onboardingCompleted: false,
  );
  @override
  Future<Map<String, dynamic>?> questionnaire() async =>
      savedAnswers == null ? null : {'completed': true};
  @override
  Future<List<dynamic>> photos() async => [];
  @override
  Future<List<dynamic>> consents() async => [];
  @override
  Future<List<dynamic>> analyses() async => [];
  @override
  Future<void> saveConsent(String type, bool granted) async {
    decisions[type] = granted;
  }

  @override
  Future<void> saveQuestionnaire(Map<String, String> answers) async {
    savedAnswers = Map.from(answers);
  }

  @override
  Future<Map<String, dynamic>> buildProfile() async => {
    'perceived_skin_type': null,
    'sensitivity': null,
    'main_concerns': [],
  };
  @override
  Future<RoutineDay> routineToday({DateTime? date}) async => RoutineDay(
    date: date ?? DateTime.now(),
    allowedSteps: const {
      'AM': ['limpiador', 'hidratante', 'protector_solar'],
      'PM': ['limpiador', 'hidratante'],
    },
    streakDays: 3,
  );
  @override
  Future<RoutineLog> checkin({
    required String period,
    required List<String> completedSteps,
    String notes = '',
  }) async => RoutineLog(
    period: period,
    completedSteps: completedSteps,
    notes: notes,
    completed: false,
  );
}

void main() {
  testWidgets('rejects public HTTP before sending account credentials', (
    tester,
  ) async {
    final api = FakeApi();
    await tester.pumpWidget(AsesorIaApp(api: api));
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Correo'),
      'test@example.org',
    );
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Contraseña'),
      'test-password',
    );
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Dirección del servidor'),
      'http://10.attacker.example',
    );
    await tester.ensureVisible(find.text('Entrar'));
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();
    expect(api.signedIn, isFalse);
    expect(
      find.text(
        'Usa una dirección HTTPS, o HTTP para el servidor de pruebas en tu red local.',
      ),
      findsOneWidget,
    );
  });
  testWidgets('requires login before showing personal content', (tester) async {
    await tester.pumpWidget(AsesorIaApp(api: FakeApi()));
    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Seguimiento diario'), findsNothing);
    expect(find.text('Contraseña'), findsOneWidget);
  });
  testWidgets('login opens isolated dashboard and logout returns to login', (
    tester,
  ) async {
    final api = FakeApi();
    await tester.pumpWidget(AsesorIaApp(api: api));
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Correo'),
      'test@example.org',
    );
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Contraseña'),
      'test-password',
    );
    await tester.ensureVisible(find.text('Entrar'));
    await tester.tap(find.text('Entrar'));
    await tester.pumpAndSettle();
    expect(find.text('Hola, Ana'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Racha: 3 días'), 250);
    expect(find.text('Racha: 3 días'), findsOneWidget);
    await tester.tap(find.byTooltip('Cerrar sesión'));
    await tester.pumpAndSettle();
    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Hola, Ana'), findsNothing);
  });
  testWidgets(
    'questionnaire can be completed without photos or forced answers',
    (tester) async {
      final api = FakeApi();
      await tester.pumpWidget(MaterialApp(home: QuestionnairePage(api: api)));
      for (var i = 0; i < 6; i++) {
        await tester.scrollUntilVisible(find.text('Continuar'), 200);
        await tester.tap(find.text('Continuar'));
        await tester.pumpAndSettle();
      }
      await tester.ensureVisible(find.text('Guardar mi perfil'));
      await tester.tap(find.text('Guardar mi perfil'));
      await tester.pumpAndSettle();
      expect(api.savedAnswers?.length, 7);
      expect(api.savedAnswers?['irritates_easily'], 'No estoy seguro');
    },
  );
  testWidgets(
    'training preference starts unchecked and service stays independent',
    (tester) async {
      final api = FakeApi();
      await tester.pumpWidget(MaterialApp(home: ConsentPage(api: api)));
      await tester.pumpAndSettle();
      final switches = tester.widgetList<Switch>(find.byType(Switch)).toList();
      expect(switches.length, 2);
      expect(switches.every((s) => !s.value), isTrue);
      await tester.tap(find.byType(Switch).first);
      await tester.ensureVisible(find.text('Guardar mis decisiones'));
      await tester.tap(find.text('Guardar mis decisiones'));
      await tester.pumpAndSettle();
      expect(api.decisions, {'service': true, 'training': false});
    },
  );
}
