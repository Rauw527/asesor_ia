import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../controllers/inci_controller.dart';
import '../models/inci_scan.dart';
import '../widgets/camera_capture_view.dart';

/// Label scanner: OCR through Gemini + deterministic conflict rules.
class InciScannerPage extends StatelessWidget {
  const InciScannerPage({super.key});

  Future<void> _handleImage(BuildContext context, Uint8List bytes) async {
    final controller = context.read<InciController>();
    final result = await controller.scanLabel(bytes);
    if (!context.mounted || result != null) return;

    final message = controller.error ?? 'No pudimos leer la etiqueta.';
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('No pudimos analizar el producto'),
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

  Future<void> _addToRoutine(BuildContext context) async {
    final controller = context.read<InciController>();
    final saved = await controller.addToRoutine();
    if (!context.mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(
            saved
                ? 'Producto añadido a tu rutina activa.'
                : controller.error ?? 'No se pudo guardar el producto.',
          ),
        ),
      );
  }

  Future<void> _openLink(BuildContext context, String link) async {
    final uri = Uri.tryParse(link);
    if (uri == null || !uri.hasScheme) return;
    try {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (_) {
      // No-op: a dead affiliate link must not break the audit flow.
    }
  }

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<InciController>();
    final scan = controller.scan;

    if (scan == null) {
      return Scaffold(
        backgroundColor: Colors.black,
        extendBodyBehindAppBar: true,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
          elevation: 0,
          title: const Text('Auditar INCI'),
        ),
        body: CameraCaptureView(
          onImageCaptured: (bytes) => _handleImage(context, bytes),
          busy: controller.scanning,
          useFrontCamera: false,
          showOval: false,
          hint: 'Encuadra la lista de ingredientes (INCI) de la etiqueta',
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Auditoría INCI')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        children: [
          if (controller.labelImage != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: SizedBox(
                height: 160,
                width: double.infinity,
                child: Image.memory(
                  controller.labelImage!,
                  fit: BoxFit.cover,
                  gaplessPlayback: true,
                ),
              ),
            ),
          const SizedBox(height: 18),
          Text(
            scan.productName,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 14),
          _ConflictBanner(scan: scan),
          if (scan.keyIngredients.isNotEmpty) ...[
            const SizedBox(height: 22),
            const _SectionTitle('Ingredientes clave'),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final ingredient in scan.keyIngredients)
                  Chip(label: Text(ingredient)),
              ],
            ),
          ],
          if (scan.safeAlternative != null) ...[
            const SizedBox(height: 22),
            const _SectionTitle('Alternativa segura'),
            _AlternativeCard(
              alternative: scan.safeAlternative!,
              onOpen: () =>
                  _openLink(context, scan.safeAlternative!.affiliateLink),
            ),
          ],
          if (controller.error != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.errorContainer,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Text(controller.error!),
            ),
          ],
          const SizedBox(height: 24),
          if (scan.keyIngredients.isNotEmpty)
            FilledButton.icon(
              onPressed: controller.saved || controller.saving
                  ? null
                  : () => _addToRoutine(context),
              icon: Icon(controller.saved ? Icons.check : Icons.playlist_add),
              label: Text(
                controller.saved ? 'Añadido a tu rutina' : 'Añadir a mi rutina',
              ),
            ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: controller.reset,
            icon: const Icon(Icons.document_scanner_outlined),
            label: const Text('Escanear otro producto'),
          ),
          const SizedBox(height: 20),
          Text(
            'Guardar el producto permite detectar conflictos con tus próximas '
            'compras. La auditoría es informativa y no sustituye la opinión de '
            'un dermatólogo.',
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

class _ConflictBanner extends StatelessWidget {
  const _ConflictBanner({required this.scan});

  final InciScan scan;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final conflict = scan.hasConflict;
    final background = conflict
        ? theme.colorScheme.errorContainer
        : const Color(0xFFE6F4EA);
    final foreground = conflict
        ? theme.colorScheme.onErrorContainer
        : const Color(0xFF1E6B33);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            conflict ? Icons.warning_amber_rounded : Icons.verified_outlined,
            color: foreground,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  conflict ? 'Conflicto detectado' : 'Sin conflictos',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: foreground,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  scan.conflictWarning ??
                      'Ninguno de los ingredientes clave choca con tu rutina '
                          'activa.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: foreground,
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

class _AlternativeCard extends StatelessWidget {
  const _AlternativeCard({required this.alternative, required this.onOpen});

  final SafeAlternative alternative;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.spa_outlined,
                  size: 18,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    alternative.name,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              alternative.reason,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                height: 1.4,
              ),
            ),
            if (alternative.affiliateLink.isNotEmpty) ...[
              const SizedBox(height: 6),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton.icon(
                  onPressed: onOpen,
                  icon: const Icon(Icons.open_in_new, size: 16),
                  label: const Text('Ver producto'),
                ),
              ),
            ],
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
