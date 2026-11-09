import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/skin_controller.dart';
import '../controllers/user_controller.dart';
import '../widgets/camera_capture_view.dart';
import 'skin_result_page.dart';

/// Full-screen capture flow for the facial diagnosis.
class FaceScannerPage extends StatefulWidget {
  const FaceScannerPage({super.key});

  @override
  State<FaceScannerPage> createState() => _FaceScannerPageState();
}

class _FaceScannerPageState extends State<FaceScannerPage> {
  Future<void> _handleImage(Uint8List bytes) async {
    final skin = context.read<SkinController>();
    final result = await skin.analyze(bytes);
    if (!mounted) return;

    if (result == null) {
      final message =
          skin.error ?? 'No pudimos analizar la imagen. Prueba con otra selfie.';
      await showDialog<void>(
        context: context,
        builder: (dialogContext) => AlertDialog(
          title: const Text('No pudimos analizar la foto'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Entendido'),
            ),
          ],
        ),
      );
      return;
    }

    // The diagnosis also updates the stored profile.
    context.read<UserController>().refreshAfterAnalysis();

    await Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => SkinResultPage(analysis: result, image: bytes),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final analyzing = context.watch<SkinController>().analyzing;

    return Scaffold(
      backgroundColor: Colors.black,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text('Diagnóstico facial'),
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          CameraCaptureView(
            onImageCaptured: _handleImage,
            busy: analyzing,
            hint: 'Luz natural, sin maquillaje y mirando al frente',
          ),
          if (analyzing)
            Positioned(
              left: 20,
              right: 20,
              bottom: 120,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.75),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Row(
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Analizando tu piel con Gemini… puede tardar unos segundos.',
                        style: TextStyle(color: Colors.white, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
