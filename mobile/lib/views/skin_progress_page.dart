import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/progress_controller.dart';
import '../utils/spanish_date.dart';
import '../widgets/before_after_slider.dart';
import '../widgets/camera_capture_view.dart';
import '../widgets/metric_card.dart';

enum _CaptureMode { none, baseline, current }

/// Day 1 vs. today: local baseline photo, real multimodal comparison.
class SkinProgressPage extends StatefulWidget {
  const SkinProgressPage({super.key});

  @override
  State<SkinProgressPage> createState() => _SkinProgressPageState();
}

class _SkinProgressPageState extends State<SkinProgressPage> {
  _CaptureMode _mode = _CaptureMode.none;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<ProgressController>().loadBaseline();
    });
  }

  Future<void> _handleCapture(Uint8List bytes) async {
    final controller = context.read<ProgressController>();
    final mode = _mode;

    if (mode == _CaptureMode.baseline) {
      final saved = await controller.setBaseline(bytes);
      if (!mounted) return;
      setState(() => _mode = _CaptureMode.none);
      _snack(
        saved
            ? 'Foto Día 1 guardada. Vuelve en unas semanas para comparar.'
            : controller.error ?? 'No se pudo guardar la foto.',
      );
      return;
    }

    final result = await controller.compare(bytes);
    if (!mounted) return;
    setState(() => _mode = _CaptureMode.none);

    if (result == null) {
      final message = controller.error ?? 'No pudimos comparar las fotos.';
      await showDialog<void>(
        context: context,
        builder: (dialogContext) => AlertDialog(
          title: const Text('No pudimos comparar'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Entendido'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _confirmReset(ProgressController controller) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('¿Cambiar la foto Día 1?'),
        content: const Text(
          'Se borrará la referencia actual y la comparativa guardada en este '
          'dispositivo.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Cambiar'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    await controller.resetBaseline();
    if (!mounted) return;
    _snack(controller.error ?? 'Línea base eliminada.');
  }

  void _snack(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<ProgressController>();

    if (_mode != _CaptureMode.none) {
      final isBaseline = _mode == _CaptureMode.baseline;
      return Scaffold(
        backgroundColor: Colors.black,
        extendBodyBehindAppBar: true,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          elevation: 0,
          title: Text(isBaseline ? 'Foto Día 1' : 'Foto de hoy'),
        ),
        body: CameraCaptureView(
          onImageCaptured: _handleCapture,
          busy: controller.comparing,
          hint: isBaseline
              ? 'Encuadra tu rostro para guardar la referencia'
              : 'Misma luz y ángulo que tu foto Día 1',
        ),
      );
    }

    final result = controller.result;
    final baseline = controller.baselineBytes;
    final current = controller.currentBytes;

    return Scaffold(
      appBar: AppBar(title: const Text('Mi progreso')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        children: [
          if (controller.loading && baseline == null)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(child: CircularProgressIndicator()),
            )
          else
            _BaselineCard(
              controller: controller,
              onCapture: () => setState(() => _mode = _CaptureMode.baseline),
              onReset: () => _confirmReset(controller),
            ),
          if (controller.hasBaseline) ...[
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () => setState(() => _mode = _CaptureMode.current),
              icon: const Icon(Icons.add_a_photo_outlined),
              label: const Text('Tomar foto de hoy y comparar'),
            ),
          ],
          if (controller.error != null) ...[
            const SizedBox(height: 16),
            _ErrorNote(message: controller.error!),
          ],
          if (result != null && baseline != null && current != null) ...[
            const SizedBox(height: 24),
            const _SectionTitle('Comparativa Día 1 vs. hoy'),
            BeforeAfterSlider(before: baseline, after: current),
            const SizedBox(height: 8),
            Text(
              'Desliza para revelar tu evolución.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 20),
            MetricCard(
              label: 'Progreso general',
              value: '${result.progressPercentage}%',
              caption: 'Mejora estimada por el análisis multimodal',
              icon: Icons.trending_up,
              progress: result.progressPercentage / 100,
            ),
            const SizedBox(height: 12),
            MetricCard(
              label: 'Hidratación',
              value: result.hydrationChange,
              icon: Icons.water_drop_outlined,
            ),
            const SizedBox(height: 12),
            MetricCard(
              label: 'Textura',
              value: result.textureImprovement,
              icon: Icons.blur_on,
            ),
            const SizedBox(height: 20),
            const _SectionTitle('Resumen'),
            Text(
              result.summaryNotes,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(height: 1.5),
            ),
            if (result.recommendedRoutineAdjustments.isNotEmpty) ...[
              const SizedBox(height: 20),
              const _SectionTitle('Ajustes sugeridos'),
              for (final adjustment in result.recommendedRoutineAdjustments)
                _BulletRow(text: adjustment),
            ],
          ] else if (controller.hasBaseline) ...[
            const SizedBox(height: 24),
            const _HintCard(
              icon: Icons.insights_outlined,
              title: '¿Cómo mide tu evolución?',
              body:
                  'Guardamos tu foto del Día 1 en este dispositivo. Cuando '
                  'tomes la foto de hoy, la app compara ambas imágenes con '
                  'Gemini Vision y calcula el progreso de hidratación y textura.',
            ),
          ],
          const SizedBox(height: 24),
          Text(
            'Las fotos se guardan solo en tu dispositivo. Solo se envían a la '
            'API en el momento de analizarlas o compararlas.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}

class _BaselineCard extends StatelessWidget {
  const _BaselineCard({
    required this.controller,
    required this.onCapture,
    required this.onReset,
  });

  final ProgressController controller;
  final VoidCallback onCapture;
  final VoidCallback onReset;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bytes = controller.baselineBytes;

    if (bytes == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.flag_outlined, color: theme.colorScheme.primary),
                  const SizedBox(width: 8),
                  Text('Tu foto Día 1', style: theme.textTheme.titleMedium),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                'Necesitas una foto de referencia para medir tu evolución '
                'mensual. Tómala con buena luz, sin maquillaje y mirando al '
                'frente. Se guardará solo en tu teléfono.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: onCapture,
                icon: const Icon(Icons.camera_alt_outlined),
                label: const Text('Capturar foto Día 1'),
              ),
            ],
          ),
        ),
      );
    }

    final date = controller.baselineDate;
    final days = controller.daysSinceBaseline;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Image.memory(
                bytes,
                width: 64,
                height: 64,
                fit: BoxFit.cover,
                gaplessPlayback: true,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Foto Día 1',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    date == null
                        ? 'Referencia guardada'
                        : '${shortDate(date)} · ${days ?? 0} días de seguimiento',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            TextButton(onPressed: onReset, child: const Text('Cambiar')),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Text(
        text,
        style: Theme.of(
          context,
        ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
      ),
    );
  }
}

class _BulletRow extends StatelessWidget {
  const _BulletRow({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                shape: BoxShape.circle,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}

class _HintCard extends StatelessWidget {
  const _HintCard({
    required this.icon,
    required this.title,
    required this.body,
  });

  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: theme.colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  body,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorNote extends StatelessWidget {
  const _ErrorNote({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: theme.colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(
        message,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onErrorContainer,
        ),
      ),
    );
  }
}
