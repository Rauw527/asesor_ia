import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../config/app_config.dart';
import '../controllers/routine_controller.dart';
import '../services/api_client.dart';
import '../services/asesor_api.dart';
import '../models/routine.dart';

String errorText(Object error) => error is ApiException
    ? error.message
    : 'No se pudo completar la operación. Inténtalo de nuevo.';

class AuthPage extends StatefulWidget {
  const AuthPage({super.key, required this.api, required this.onLogin});
  final AsesorApi api;
  final VoidCallback onLogin;
  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final form = GlobalKey<FormState>();
  final name = TextEditingController();
  final email = TextEditingController();
  final password = TextEditingController();
  final server = TextEditingController(text: AppConfig.apiBaseUrl);
  bool registering = false, busy = false;
  String? error;
  @override
  void dispose() {
    name.dispose();
    email.dispose();
    password.dispose();
    server.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (!form.currentState!.validate() || busy) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final uri = Uri.parse(server.text.trim());
      final host = uri.host;
      final parts = host.split('.');
      final numbers = parts.map(int.tryParse).toList();
      final ipv4 =
          parts.length == 4 &&
          numbers.every((n) => n != null && n >= 0 && n <= 255);
      final local =
          host == 'localhost' ||
          (ipv4 &&
              (numbers[0] == 127 ||
                  numbers[0] == 10 ||
                  (numbers[0] == 192 && numbers[1] == 168) ||
                  (numbers[0] == 172 &&
                      numbers[1]! >= 16 &&
                      numbers[1]! <= 31)));
      if (!uri.hasAuthority ||
          uri.userInfo.isNotEmpty ||
          (uri.path.isNotEmpty && uri.path != '/') ||
          uri.hasQuery ||
          uri.hasFragment ||
          (uri.scheme != 'https' && !(uri.scheme == 'http' && local))) {
        throw ApiException(
          'Usa una dirección HTTPS, o HTTP para el servidor de pruebas en tu red local.',
        );
      }
      AppConfig.serverOverride = uri
          .replace(path: '')
          .toString()
          .replaceAll(RegExp(r'/$'), '');
      if (registering) {
        await widget.api.register(
          name.text.trim(),
          email.text.trim(),
          password.text,
        );
      }
      await widget.api.login(email.text.trim(), password.text);
      if (mounted) widget.onLogin();
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Form(
              key: form,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.spa_outlined, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    'Facial y Moda',
                    style: Theme.of(context).textTheme.headlineMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Tu rutina, paso a paso',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  const Notice(
                    'Demo de orientación cosmética para adultos. El perfil se basa en tus respuestas; todavía no hay un modelo visual validado.',
                  ),
                  const SizedBox(height: 20),
                  if (registering)
                    TextFormField(
                      controller: name,
                      decoration: const InputDecoration(labelText: 'Nombre'),
                      validator: (v) => (v?.trim().length ?? 0) < 2
                          ? 'Escribe tu nombre'
                          : null,
                    ),
                  TextFormField(
                    controller: email,
                    decoration: const InputDecoration(labelText: 'Correo'),
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                    validator: (v) => !(v?.contains('@') ?? false)
                        ? 'Escribe un correo válido'
                        : null,
                  ),
                  TextFormField(
                    controller: password,
                    decoration: const InputDecoration(labelText: 'Contraseña'),
                    obscureText: true,
                    enableSuggestions: false,
                    autocorrect: false,
                    validator: (v) => (v?.length ?? 0) < 8
                        ? 'Usa al menos 8 caracteres'
                        : null,
                  ),
                  const SizedBox(height: 16),
                  ExpansionTile(
                    title: const Text('Conexión con el servidor'),
                    initiallyExpanded: true,
                    children: [
                      TextFormField(
                        controller: server,
                        decoration: const InputDecoration(
                          labelText: 'Dirección del servidor',
                          hintText: 'http://192.168.1.20:8000',
                        ),
                        keyboardType: TextInputType.url,
                        autocorrect: false,
                        validator: (v) =>
                            (v?.isEmpty ?? true) ? 'Indica el servidor' : null,
                      ),
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        child: Text(
                          'En un teléfono usa la IP del PC en la misma red Wi-Fi. El PC debe tener el servidor encendido.',
                        ),
                      ),
                    ],
                  ),
                  if (error != null) ErrorNotice(error!),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: busy ? null : submit,
                    child: Text(
                      busy
                          ? 'Conectando…'
                          : registering
                          ? 'Crear mi cuenta'
                          : 'Entrar',
                    ),
                  ),
                  TextButton(
                    onPressed: busy
                        ? null
                        : () => setState(() {
                            registering = !registering;
                            error = null;
                          }),
                    child: Text(
                      registering
                          ? 'Ya tengo una cuenta'
                          : 'Quiero crear una cuenta',
                    ),
                  ),
                  const Text(
                    'La sesión se conserva en memoria. Al cerrar la app tendrás que volver a entrar.',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

class DemoHomePage extends StatefulWidget {
  const DemoHomePage({super.key, required this.api, required this.onLogout});
  final AsesorApi api;
  final VoidCallback onLogout;
  @override
  State<DemoHomePage> createState() => _DemoHomePageState();
}

class _DemoHomePageState extends State<DemoHomePage> {
  String name = '';
  bool loading = true, hasQuestionnaire = false;
  int photoCount = 0;
  String? error;
  late final RoutineController tracker;
  @override
  void initState() {
    super.initState();
    tracker = RoutineController(widget.api);
    load();
  }

  @override
  void dispose() {
    tracker.dispose();
    super.dispose();
  }

  Future<void> load() async {
    if (mounted) {
      setState(() {
        loading = true;
        error = null;
      });
    }
    try {
      final user = await widget.api.me();
      final questionnaire = await widget.api.questionnaire();
      final photos = await widget.api.photos();
      await tracker.load();
      if (mounted) {
        setState(() {
          name = user.displayName;
          hasQuestionnaire =
              questionnaire != null && questionnaire['completed'] == true;
          photoCount = photos.length;
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> open(Widget page) async {
    await Navigator.of(
      context,
    ).push(MaterialPageRoute<void>(builder: (_) => page));
    if (mounted) await load();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Facial y Moda'),
      actions: [
        IconButton(
          onPressed: widget.onLogout,
          icon: const Icon(Icons.logout),
          tooltip: 'Cerrar sesión',
        ),
      ],
    ),
    body: RefreshIndicator(
      onRefresh: load,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            name.isEmpty ? 'Tu espacio de cuidado' : 'Hola, $name',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          const Text('Una rutina sencilla, con tus decisiones bajo control.'),
          const SizedBox(height: 20),
          const Notice(
            'Modo demostración. No se envían fotos a Gemini y no se mide hidratación ni mejora clínica.',
          ),
          if (loading) const LinearProgressIndicator(),
          if (error != null) ErrorNotice(error!),
          const SizedBox(height: 16),
          ActionCard(
            icon: Icons.assignment_outlined,
            title: hasQuestionnaire
                ? 'Actualizar mi cuestionario'
                : '1. Cuéntanos sobre tu piel',
            subtitle:
                'Tipo percibido, sensibilidad, tiempo y presupuesto. Puedes elegir «No sé».',
            onTap: () => open(QuestionnairePage(api: widget.api)),
          ),
          ActionCard(
            icon: Icons.wb_sunny_outlined,
            title: 'Mi perfil y mis rutinas',
            subtitle: hasQuestionnaire
                ? 'Generar una guía de mañana y noche a partir de tus respuestas.'
                : 'Primero completa el cuestionario.',
            onTap: hasQuestionnaire
                ? () => open(ResultsPage(api: widget.api))
                : null,
          ),
          ActionCard(
            icon: Icons.camera_alt_outlined,
            title: 'Mis fotografías · $photoCount',
            subtitle:
                'Opcionales. Tres vistas con revisión antes de guardarlas.',
            onTap: () => open(CapturePage(api: widget.api)),
          ),
          ActionCard(
            icon: Icons.privacy_tip_outlined,
            title: 'Privacidad y fotografías',
            subtitle: 'Gestionar permisos, ver tus fotos y eliminarlas.',
            onTap: () => open(PrivacyPage(api: widget.api)),
          ),
          const SizedBox(height: 20),
          Text(
            'Seguimiento diario',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const Text(
            'Marca los pasos que realizaste. Una racha cuenta días con al menos un período completo.',
          ),
          ListenableBuilder(
            listenable: tracker,
            builder: (context, _) => Column(
              children: [
                if (tracker.loading) const LinearProgressIndicator(),
                if (tracker.error != null) ErrorNotice(tracker.error!),
                Text('Racha: ${tracker.streakDays} días'),
                for (final period in ['AM', 'PM'])
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        children: [
                          Text(
                            period == 'AM' ? 'Mañana' : 'Noche',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          for (final step in tracker.stepsFor(period))
                            CheckboxListTile(
                              title: Text(routineStepLabels[step] ?? step),
                              value: tracker
                                  .completedFor(period)
                                  .contains(step),
                              onChanged: loading
                                  ? null
                                  : (_) => tracker.toggle(period, step),
                            ),
                          if (tracker.savingPeriod(period))
                            const LinearProgressIndicator(),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class QuestionnairePage extends StatefulWidget {
  const QuestionnairePage({super.key, required this.api});
  final AsesorApi api;
  @override
  State<QuestionnairePage> createState() => _QuestionnairePageState();
}

class _QuestionnairePageState extends State<QuestionnairePage> {
  static const questions = [
    (
      'skin_feeling',
      '¿Cómo percibes tu piel?',
      ['Grasa', 'Seca', 'Mixta', 'Normal', 'No estoy seguro'],
    ),
    (
      'after_washing',
      '¿Cómo se siente después de lavarla?',
      [
        'Tirante o seca',
        'Normal',
        'Grasa rápidamente',
        'Distinta según la zona',
        'No estoy seguro',
      ],
    ),
    (
      'irritates_easily',
      '¿Se irrita con facilidad?',
      ['Sí', 'No', 'Algunas veces', 'No estoy seguro'],
    ),
    (
      'main_concern',
      '¿Qué te preocupa principalmente?',
      [
        'Sequedad',
        'Brillo excesivo',
        'Manchas',
        'Acné',
        'Sensibilidad',
        'Ninguna',
        'No estoy seguro',
      ],
    ),
    (
      'sunscreen',
      '¿Usas protector solar?',
      ['Sí', 'No', 'Algunas veces', 'No estoy seguro'],
    ),
    (
      'time',
      '¿Cuánto tiempo deseas dedicar?',
      [
        'Menos de 5 minutos',
        '5–10 minutos',
        'Más de 10 minutos',
        'No estoy seguro',
      ],
    ),
    (
      'budget',
      '¿Qué presupuesto prefieres?',
      ['Bajo', 'Medio', 'Alto', 'Sin definir'],
    ),
  ];
  final Map<String, String> answers = {};
  int step = 0;
  bool busy = false;
  String? error;
  Future<void> save() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await widget.api.saveQuestionnaire(answers);
      await widget.api.buildProfile();
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final question = questions[step];
    return Scaffold(
      appBar: AppBar(title: const Text('Tu cuestionario')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Paso ${step + 1} de ${questions.length}'),
          LinearProgressIndicator(value: (step + 1) / questions.length),
          const SizedBox(height: 24),
          Text(question.$2, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 16),
          for (final option in question.$3)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: OutlinedButton(
                onPressed: busy
                    ? null
                    : () => setState(() => answers[question.$1] = option),
                style: OutlinedButton.styleFrom(
                  backgroundColor: answers[question.$1] == option
                      ? Theme.of(context).colorScheme.primaryContainer
                      : null,
                ),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(option),
                ),
              ),
            ),
          const Text(
            'Son datos declarados por ti, no una evaluación clínica. Puedes omitir una pregunta.',
          ),
          if (error != null) ErrorNotice(error!),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: busy
                ? null
                : () {
                    answers.putIfAbsent(question.$1, () => 'No estoy seguro');
                    if (step == questions.length - 1) {
                      save();
                    } else {
                      setState(() => step++);
                    }
                  },
            child: Text(
              busy
                  ? 'Guardando…'
                  : step == questions.length - 1
                  ? 'Guardar mi perfil'
                  : 'Continuar',
            ),
          ),
          if (step > 0)
            TextButton(
              onPressed: busy ? null : () => setState(() => step--),
              child: const Text('Anterior'),
            ),
        ],
      ),
    );
  }
}

class ResultsPage extends StatefulWidget {
  const ResultsPage({super.key, required this.api});
  final AsesorApi api;
  @override
  State<ResultsPage> createState() => _ResultsPageState();
}

class _ResultsPageState extends State<ResultsPage> {
  Map<String, dynamic>? profile;
  List<Map<String, dynamic>> plans = [];
  String? error;
  bool busy = true;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final result = await widget.api.buildProfile();
      final morning = await widget.api.recommend('morning');
      final night = await widget.api.recommend('night');
      if (mounted) {
        setState(() {
          profile = result;
          plans = [morning, night];
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tu perfil y rutina')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        if (busy) const LinearProgressIndicator(),
        if (error != null) ...[
          ErrorNotice(error!),
          FilledButton(onPressed: load, child: const Text('Reintentar')),
        ],
        if (profile != null) ...[
          Text(
            'Lo que nos contaste',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          Text(
            'Tipo de piel percibido: ${profile!['perceived_skin_type'] ?? 'No determinado'}',
          ),
          Text(
            'Sensibilidad declarada: ${profile!['sensitivity'] ?? 'No determinada'}',
          ),
          Text(
            'Preocupaciones: ${(profile!['main_concerns'] as List).join(', ')}',
          ),
          const SizedBox(height: 16),
          const Notice(
            'Estas rutinas usan reglas básicas de demostración. No hay análisis visual validado, selección de tratamientos ni recomendaciones clínicas. No sustituyen atención profesional.',
          ),
          const SizedBox(height: 16),
          for (final plan in plans)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      plan['routine_type'] == 'morning' ? 'Mañana' : 'Noche',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    for (final raw in plan['steps'] as List) ...[
                      const SizedBox(height: 12),
                      Text(
                        '${raw['order']}. ${raw['title']}',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      Text(raw['explanation'] as String),
                    ],
                    const SizedBox(height: 12),
                    Text(
                      (plan['steps'] as List).first['preference_note']
                              as String? ??
                          '',
                    ),
                  ],
                ),
              ),
            ),
        ],
      ],
    ),
  );
}

class ConsentPage extends StatefulWidget {
  const ConsentPage({super.key, required this.api});
  final AsesorApi api;
  @override
  State<ConsentPage> createState() => _ConsentPageState();
}

class _ConsentPageState extends State<ConsentPage> {
  bool service = false, training = false, loading = true, busy = false;
  String? error;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final consents = await widget.api.consents();
      if (mounted) {
        setState(() {
          for (final c in consents) {
            if (c['consent_type'] == 'service') service = c['granted'] == true;
            if (c['consent_type'] == 'training') {
              training = c['granted'] == true;
            }
          }
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> save() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await widget.api.saveConsent('service', service);
      await widget.api.saveConsent('training', training);
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tus decisiones de privacidad')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Notice(
          'Las fotos se guardan en el servidor que elegiste, de forma privada, hasta que las elimines. Esta demo no las envía a servicios de IA ni entrena modelos.',
        ),
        if (loading) const LinearProgressIndicator(),
        SwitchListTile(
          title: const Text('A. Guardar fotos para el servicio'),
          subtitle: const Text(
            'Necesario solo para subir fotografías. Puedes usar el cuestionario y las rutinas aunque lo rechaces.',
          ),
          value: service,
          onChanged: loading || busy
              ? null
              : (v) => setState(() => service = v),
        ),
        SwitchListTile(
          title: const Text('B. Colaboración futura con entrenamiento'),
          subtitle: const Text(
            'Voluntario. Registra tu preferencia; no se exportan imágenes ni se entrena IA en esta demo. Cualquier proyecto concreto necesitará explicar su alcance antes de usar tus fotos.',
          ),
          value: training,
          onChanged: loading || busy
              ? null
              : (v) => setState(() => training = v),
        ),
        const Text(
          'Puedes retirar estas autorizaciones desactivándolas y guardando. Retirar A bloquea nuevas subidas; para borrar las fotos existentes usa «Privacidad y fotografías».',
        ),
        if (error != null) ErrorNotice(error!),
        const SizedBox(height: 20),
        FilledButton(
          onPressed: loading || busy ? null : save,
          child: Text(busy ? 'Guardando…' : 'Guardar mis decisiones'),
        ),
      ],
    ),
  );
}

class CapturePage extends StatefulWidget {
  const CapturePage({super.key, required this.api});
  final AsesorApi api;
  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  static const labels = {
    'front': 'Frente',
    'left': 'Mejilla izquierda',
    'right': 'Mejilla derecha',
  };
  final Map<String, Uint8List> images = {};
  final Map<String, String> uploaded = {};
  bool busy = false;
  String? error;
  Future<void> pick(String type, ImageSource source) async {
    try {
      final photo = await ImagePicker().pickImage(
        source: source,
        preferredCameraDevice: CameraDevice.front,
        maxWidth: 1600,
        imageQuality: 90,
      );
      if (photo == null) return;
      final bytes = await photo.readAsBytes();
      if (mounted) {
        setState(() {
          images[type] = bytes;
          uploaded.remove(type);
          error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(
          () => error =
              'No se pudo abrir la cámara o galería. Revisa los permisos del teléfono.',
        );
      }
    }
  }

  Future<void> save() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final consents = await widget.api.consents();
      if (!consents.any(
        (c) => c['consent_type'] == 'service' && c['granted'] == true,
      )) {
        if (!mounted) return;
        await Navigator.of(context).push(
          MaterialPageRoute<void>(builder: (_) => ConsentPage(api: widget.api)),
        );
        if (!mounted) return;
        final updated = await widget.api.consents();
        if (!updated.any(
          (c) => c['consent_type'] == 'service' && c['granted'] == true,
        )) {
          throw ApiException(
            'No se guardó ninguna foto nueva: el permiso A está desactivado.',
          );
        }
      }
      for (final type in labels.keys) {
        if (!uploaded.containsKey(type)) {
          uploaded[type] = await widget.api.uploadPhoto(type, images[type]!);
        }
      }
      await widget.api.demoAnalysis(uploaded.values.toList());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Fotos privadas guardadas. El análisis visual permanece en modo demostración.',
            ),
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        setState(
          () => error =
              '${errorText(e)}${uploaded.isNotEmpty ? ' ${uploaded.length} foto(s) ya se guardaron; puedes revisarlas o eliminarlas en Privacidad.' : ''}',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Tus tres fotografías')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Notice(
          'Opcional. Busca luz uniforme, evita filtros y revisa cada imagen antes de guardarla. El permiso A se comprueba al enviar. No se calculan puntuaciones sobre tu piel.',
        ),
        for (final entry in labels.entries)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Text(
                    entry.value,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  if (images[entry.key] != null) ...[
                    Image.memory(
                      images[entry.key]!,
                      height: 180,
                      fit: BoxFit.contain,
                    ),
                    TextButton(
                      onPressed: busy
                          ? null
                          : () => setState(() {
                              images.remove(entry.key);
                              uploaded.remove(entry.key);
                            }),
                      child: const Text('Quitar selección'),
                    ),
                  ],
                  Wrap(
                    spacing: 8,
                    children: [
                      OutlinedButton.icon(
                        onPressed: busy
                            ? null
                            : () => pick(entry.key, ImageSource.camera),
                        icon: const Icon(Icons.camera_alt_outlined),
                        label: const Text('Cámara'),
                      ),
                      OutlinedButton.icon(
                        onPressed: busy
                            ? null
                            : () => pick(entry.key, ImageSource.gallery),
                        icon: const Icon(Icons.photo_library_outlined),
                        label: const Text('Galería'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        if (error != null) ErrorNotice(error!),
        FilledButton(
          onPressed: busy || images.length != 3 ? null : save,
          child: Text(busy ? 'Guardando…' : 'Guardar las tres fotografías'),
        ),
        TextButton(
          onPressed: busy ? null : () => Navigator.of(context).pop(),
          child: const Text('Continuar sin fotografías'),
        ),
      ],
    ),
  );
}

class PrivacyPage extends StatefulWidget {
  const PrivacyPage({super.key, required this.api});
  final AsesorApi api;
  @override
  State<PrivacyPage> createState() => _PrivacyPageState();
}

class _PrivacyPageState extends State<PrivacyPage> {
  List<dynamic> photos = [], analyses = [];
  bool busy = true;
  String? error;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final result = await widget.api.photos();
      final history = await widget.api.analyses();
      if (mounted) {
        setState(() {
          photos = result;
          analyses = history;
        });
      }
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> remove(String id) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Eliminar esta fotografía?'),
        content: const Text(
          'Se eliminará del servidor. Esta acción no se puede deshacer.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    setState(() => busy = true);
    try {
      await widget.api.deletePhoto(id);
      if (mounted) await load();
    } catch (e) {
      if (mounted) {
        setState(() {
          busy = false;
          error = errorText(e);
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Privacidad y fotografías')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Notice(
          'Solo tu cuenta puede consultar estas fotografías. Las decisiones de consentimiento se registran con fecha y versión. No hay un proceso de entrenamiento activo.',
        ),
        FilledButton.tonal(
          onPressed: busy
              ? null
              : () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => ConsentPage(api: widget.api),
                    ),
                  );
                  if (mounted) await load();
                },
          child: const Text('Gestionar consentimientos'),
        ),
        if (busy) const LinearProgressIndicator(),
        if (error != null) ...[
          ErrorNotice(error!),
          TextButton(onPressed: load, child: const Text('Reintentar')),
        ],
        const SizedBox(height: 20),
        Text('Mis fotografías', style: Theme.of(context).textTheme.titleLarge),
        if (photos.isEmpty && !busy)
          const Text('Todavía no has guardado fotografías.'),
        for (final photo in photos)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  Text(
                    '${photo['photo_type']} · ${photo['uploaded_at'].toString().split('T').first}',
                  ),
                  Image.network(
                    AppConfig.endpoint(
                      '/photos/${photo['id']}/content',
                    ).toString(),
                    headers: widget.api.authHeaders,
                    height: 160,
                    fit: BoxFit.contain,
                    errorBuilder: (_, error, stack) =>
                        const Text('No se pudo cargar esta fotografía.'),
                  ),
                  TextButton.icon(
                    onPressed: busy
                        ? null
                        : () => remove(photo['id'] as String),
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Eliminar fotografía'),
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 20),
        Text(
          'Historial de capturas',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        for (final item in analyses)
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Análisis de demostración'),
            subtitle: Text(
              '${item['created_at'].toString().split('T').first} · Sin predicciones visuales',
            ),
          ),
      ],
    ),
  );
}

class Notice extends StatelessWidget {
  const Notice(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Theme.of(
        context,
      ).colorScheme.primaryContainer.withValues(alpha: .45),
      borderRadius: BorderRadius.circular(16),
    ),
    child: Text(text),
  );
}

class ErrorNotice extends StatelessWidget {
  const ErrorNotice(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 12),
    child: Text(
      text,
      style: TextStyle(color: Theme.of(context).colorScheme.error),
    ),
  );
}

class ActionCard extends StatelessWidget {
  const ActionCard({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });
  final IconData icon;
  final String title, subtitle;
  final VoidCallback? onTap;
  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      contentPadding: const EdgeInsets.all(16),
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
      enabled: onTap != null,
    ),
  );
}
