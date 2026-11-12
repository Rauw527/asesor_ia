import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/routine_controller.dart';
import '../controllers/user_controller.dart';
import '../models/routine.dart';
import '../utils/spanish_date.dart';
import 'face_scanner_page.dart';
import 'inci_scanner_page.dart';
import 'skin_progress_page.dart';

/// Daily hub: profile snapshot, AM/PM checklist and entry points to the tools.
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<UserController>().load();
      context.read<RoutineController>().load();
    });
  }

  Future<void> _refresh() async {
    await Future.wait([
      context.read<UserController>().load(force: true),
      context.read<RoutineController>().load(),
    ]);
  }

  void _open(Widget page) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _refresh,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
            children: [
              const _Header(),
              const SizedBox(height: 20),
              const _ProfileCard(),
              const SizedBox(height: 20),
              const _RoutineCard(),
              const SizedBox(height: 20),
              _QuickActions(
                onScanFace: () => _open(const FaceScannerPage()),
                onProgress: () => _open(const SkinProgressPage()),
                onInci: () => _open(const InciScannerPage()),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = context.watch<UserController>();
    final fullName = user.profile?.fullName.trim() ?? '';
    final greeting = fullName.isEmpty
        ? 'Hola'
        : 'Hola, ${user.profile!.displayName}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.auto_awesome,
                size: 18,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'Asesor IA',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.primary,
                letterSpacing: 0.3,
              ),
            ),
            const Spacer(),
            CircleAvatar(
              radius: 20,
              backgroundColor: theme.colorScheme.secondaryContainer,
              child: Text(
                _initials(fullName),
                style: theme.textTheme.labelLarge?.copyWith(
                  color: theme.colorScheme.onSecondaryContainer,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        Text(greeting, style: theme.textTheme.headlineMedium),
        const SizedBox(height: 4),
        Text(
          longSpanishDate(DateTime.now()),
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  String _initials(String name) {
    if (name.isEmpty) return 'AI';
    final parts = name
        .split(RegExp(r'\s+'))
        .where((p) => p.isNotEmpty)
        .toList();
    if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
    final first = parts.first.substring(0, 1);
    final last = parts.last.substring(0, 1);
    return (first + last).toUpperCase();
  }
}

class _ProfileCard extends StatelessWidget {
  const _ProfileCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final user = context.watch<UserController>();
    final profile = user.skinProfile;

    if (user.loading && user.profile == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    if (profile == null || profile.skinType == null) {
      // No analysis yet: invite the user to run the first one.
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.face_retouching_natural,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Text('Tu piel', style: theme.textTheme.titleMedium),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                'Aún no conocemos tu tipo de piel. Haz tu primer diagnóstico '
                'con una selfie y desbloquea tu rutina personalizada.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              if (user.error != null) ...[
                const SizedBox(height: 10),
                Text(
                  user.error!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.error,
                  ),
                ),
                const SizedBox(height: 6),
                TextButton(
                  onPressed: () =>
                      context.read<UserController>().load(force: true),
                  child: const Text('Reintentar'),
                ),
              ],
              const SizedBox(height: 14),
              FilledButton.icon(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const FaceScannerPage()),
                ),
                icon: const Icon(Icons.camera_alt_outlined),
                label: const Text('Escanear mi rostro'),
              ),
            ],
          ),
        ),
      );
    }

    final issues = profile.detectedIssues;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.face_retouching_natural,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text('Tu piel', style: theme.textTheme.titleMedium),
                const Spacer(),
                TextButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const FaceScannerPage()),
                  ),
                  child: const Text('Actualizar'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _MiniStat(
                    label: 'Tipo',
                    value: profile.skinType ?? '—',
                  ),
                ),
                Expanded(
                  child: _MiniStat(
                    label: 'Subtono',
                    value: profile.undertone ?? '—',
                  ),
                ),
                Expanded(
                  child: _MiniStat(
                    label: 'Hidratación',
                    value: profile.hydrationLevel == null
                        ? '—'
                        : '${profile.hydrationLevel}%',
                  ),
                ),
              ],
            ),
            if (profile.hydrationLevel != null) ...[
              const SizedBox(height: 14),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: (profile.hydrationLevel! / 100)
                      .clamp(0.0, 1.0)
                      .toDouble(),
                  minHeight: 7,
                ),
              ),
            ],
            if (issues.isNotEmpty) ...[
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final issue in issues.take(4))
                    Chip(
                      label: Text(issue),
                      visualDensity: VisualDensity.compact,
                    ),
                  if (issues.length > 4)
                    Chip(
                      label: Text('+${issues.length - 4}'),
                      visualDensity: VisualDensity.compact,
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  const _MiniStat({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          value,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}

class _RoutineCard extends StatelessWidget {
  const _RoutineCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final routine = context.watch<RoutineController>();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.today_outlined, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text('Rutina de hoy', style: theme.textTheme.titleMedium),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF1E0),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.local_fire_department,
                        size: 16,
                        color: Color(0xFFE07A2F),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${routine.streakDays} días',
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: const Color(0xFFB15B18),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (routine.loading && routine.day == null) ...[
              const SizedBox(height: 16),
              const LinearProgressIndicator(),
            ],
            if (routine.error != null) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      routine.error!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.read<RoutineController>().load(),
                    child: const Text('Reintentar'),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 8),
            _PeriodChecklist(period: 'AM', title: 'Mañana'),
            const Divider(height: 24),
            _PeriodChecklist(period: 'PM', title: 'Noche'),
          ],
        ),
      ),
    );
  }
}

class _PeriodChecklist extends StatelessWidget {
  const _PeriodChecklist({required this.period, required this.title});

  final String period;
  final String title;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final routine = context.watch<RoutineController>();
    final steps = routine.stepsFor(period);
    final completed = routine.completedFor(period);
    final progress = routine.progressFor(period);
    final done = routine.isPeriodComplete(period);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              title,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${completed.where(steps.contains).length}/${steps.length}',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const Spacer(),
            if (routine.savingPeriod(period))
              const SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            else if (done)
              Row(
                children: [
                  const Icon(
                    Icons.check_circle,
                    size: 15,
                    color: Color(0xFF2E7D32),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Completado',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: const Color(0xFF2E7D32),
                    ),
                  ),
                ],
              ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(value: progress, minHeight: 4),
        ),
        const SizedBox(height: 4),
        for (final step in steps)
          CheckboxListTile(
            value: completed.contains(step),
            onChanged: (_) =>
                context.read<RoutineController>().toggle(period, step),
            title: Text(routineStepLabels[step] ?? step),
            dense: true,
            contentPadding: EdgeInsets.zero,
            visualDensity: VisualDensity.compact,
            controlAffinity: ListTileControlAffinity.leading,
          ),
      ],
    );
  }
}

class _QuickActions extends StatelessWidget {
  const _QuickActions({
    required this.onScanFace,
    required this.onProgress,
    required this.onInci,
  });

  final VoidCallback onScanFace;
  final VoidCallback onProgress;
  final VoidCallback onInci;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          _ActionTile(
            icon: Icons.face_retouching_natural,
            title: 'Diagnóstico facial',
            subtitle: 'Analiza tu piel con una selfie',
            onTap: onScanFace,
          ),
          const Divider(height: 1, indent: 68),
          _ActionTile(
            icon: Icons.timeline,
            title: 'Mi progreso',
            subtitle: 'Compara el Día 1 con hoy',
            onTap: onProgress,
          ),
          const Divider(height: 1, indent: 68),
          _ActionTile(
            icon: Icons.document_scanner_outlined,
            title: 'Auditar INCI',
            subtitle: 'Detecta conflictos de ingredientes',
            onTap: onInci,
          ),
        ],
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  const _ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListTile(
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      leading: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: theme.colorScheme.primary.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, color: theme.colorScheme.primary),
      ),
      title: Text(
        title,
        style: theme.textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right, size: 20),
    );
  }
}
