import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../controllers/progress_controller.dart';
import '../models/skin_analysis.dart';
import '../services/photo_store.dart';
import '../widgets/metric_card.dart';

/// Read-only presentation of the diagnosis returned by Gemini.
class SkinResultPage extends StatelessWidget {
  const SkinResultPage({super.key, required this.analysis, this.image});

  final SkinAnalysis analysis;
  final Uint8List? image;

  Future<void> _openLink(BuildContext context, String link) async {
    final uri = Uri.tryParse(link);
    if (uri == null || !uri.hasScheme) {
      _snack(context, 'Este producto aún no tiene enlace disponible.');
      return;
    }
    try {
      final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!opened && context.mounted) {
        _snack(context, 'No se pudo abrir el enlace del producto.');
      }
    } catch (_) {
      if (context.mounted) {
        _snack(context, 'No se pudo abrir el enlace del producto.');
      }
    }
  }

  Future<void> _saveBaseline(BuildContext context) async {
    final bytes = image;
    if (bytes == null) return;
    try {
      await PhotoStore().saveBaseline(bytes);
      if (!context.mounted) return;
      await context.read<ProgressController>().loadBaseline();
      if (!context.mounted) return;
      _snack(context, 'Foto guardada como Día 1 para tu comparativa.');
    } catch (_) {
      if (!context.mounted) return;
      _snack(context, 'No se pudo guardar la foto en este dispositivo.');
    }
  }

  void _snack(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hydration =
        (analysis.hydrationLevel / 100).clamp(0.0, 1.0).toDouble();

    return Scaffold(
      appBar: AppBar(title: const Text('Tu diagnóstico')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        children: [
          _Hero(image: image),
          const SizedBox(height: 20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: MetricCard(
                  label: 'Tipo de piel',
                  value: analysis.skinType,
                  icon: Icons.spa_outlined,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: MetricCard(
                  label: 'Subtono',
                  value: analysis.undertone,
                  icon: Icons.palette_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          MetricCard(
            label: 'Nivel de hidratación',
            value: '${analysis.hydrationLevel}%',
            caption: _hydrationCaption(analysis.hydrationLevel),
            icon: Icons.water_drop_outlined,
            progress: hydration,
          ),
          const SizedBox(height: 24),
          const _SectionTitle('Lo que detectamos'),
          if (analysis.detectedIssues.isEmpty)
            Text(
              'No se detectaron incidencias visibles.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            )
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final issue in analysis.detectedIssues)
                  Chip(label: Text(issue)),
              ],
            ),
          if (analysis.recommendations.isNotEmpty) ...[
            const SizedBox(height: 24),
            const _SectionTitle('Tu rutina recomendada'),
            for (var index = 0; index < analysis.recommendations.length; index++)
              _NumberedRow(
                index: index + 1,
                text: analysis.recommendations[index],
              ),
          ],
          if (analysis.productSuggestions.isNotEmpty) ...[
            const SizedBox(height: 24),
            const _SectionTitle('Productos sugeridos'),
            for (final product in analysis.productSuggestions) ...[
              _ProductCard(
                product: product,
                onOpen: () => _openLink(context, product.affiliateLink),
              ),
              const SizedBox(height: 12),
            ],
          ],
          const SizedBox(height: 20),
          _Disclaimer(text: analysis.disclaimer),
          const SizedBox(height: 24),
          if (image != null)
            OutlinedButton.icon(
              onPressed: () => _saveBaseline(context),
              icon: const Icon(Icons.bookmark_add_outlined),
              label: const Text('Guardar como foto Día 1'),
            ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () =>
                Navigator.of(context).popUntil((route) => route.isFirst),
            child: const Text('Listo'),
          ),
        ],
      ),
    );
  }

  String _hydrationCaption(int level) {
    if (level < 35) return 'Tu piel necesita hidratación urgente.';
    if (level < 60) return 'Hidratación por debajo de lo ideal.';
    if (level < 80) return 'Buen nivel, mantén tu rutina.';
    return 'Hidratación excelente.';
  }
}

class _Hero extends StatelessWidget {
  const _Hero({required this.image});

  final Uint8List? image;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bytes = image;

    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: SizedBox(
        height: 220,
        width: double.infinity,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (bytes != null)
              Image.memory(bytes, fit: BoxFit.cover, gaplessPlayback: true)
            else
              ColoredBox(color: theme.colorScheme.secondaryContainer),
            const DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Color(0xCC000000)],
                ),
              ),
            ),
            Positioned(
              left: 20,
              right: 20,
              bottom: 18,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Tu piel hoy',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Análisis generado con Gemini Vision',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.8),
                      fontSize: 12,
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
        style: Theme.of(context)
            .textTheme
            .titleMedium
            ?.copyWith(fontWeight: FontWeight.w700),
      ),
    );
  }
}

class _NumberedRow extends StatelessWidget {
  const _NumberedRow({required this.index, required this.text});

  final int index;
  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 24,
            height: 24,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: Text(
              '$index',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w700,
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

class _ProductCard extends StatelessWidget {
  const _ProductCard({required this.product, required this.onOpen});

  final ProductSuggestion product;
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
                Expanded(
                  child: Text(
                    product.name,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    product.brand,
                    style: theme.textTheme.labelSmall,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              product.reason,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                height: 1.4,
              ),
            ),
            if (product.affiliateLink.isNotEmpty) ...[
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

class _Disclaimer extends StatelessWidget {
  const _Disclaimer({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline,
            size: 18,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
