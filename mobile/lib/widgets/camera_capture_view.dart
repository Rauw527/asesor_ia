import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/photo_store.dart';

/// Live camera with an oval framing guide and a client-side light meter.
///
/// The meter reads the mean luma of the preview stream (throttled) so the user
/// can fix poor lighting *before* spending a Gemini call. When the camera is
/// unavailable (desktop/web preview, denied permission) it degrades to the
/// gallery picker instead of blocking the flow.
class CameraCaptureView extends StatefulWidget {
  const CameraCaptureView({
    super.key,
    required this.onImageCaptured,
    this.busy = false,
    this.hint = 'Centra tu rostro dentro del óvalo',
    this.useFrontCamera = true,
    this.showOval = true,
  });

  final ValueChanged<Uint8List> onImageCaptured;
  final bool busy;
  final String hint;
  final bool useFrontCamera;
  final bool showOval;

  @override
  State<CameraCaptureView> createState() => _CameraCaptureViewState();
}

class _CameraCaptureViewState extends State<CameraCaptureView>
    with WidgetsBindingObserver {
  CameraController? _controller;
  bool _streaming = false;
  bool _initializing = true;
  bool _takingPicture = false;
  double? _luminance;
  String? _error;
  DateTime _lastMeterUpdate = DateTime.fromMillisecondsSinceEpoch(0);

  bool get _busy => widget.busy || _takingPicture;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initialize();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _disposeCamera();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_controller == null) return;
    if (state == AppLifecycleState.inactive) {
      _disposeCamera();
      if (mounted) {
        setState(() {
          _initializing = true;
          _luminance = null;
        });
      }
    } else if (state == AppLifecycleState.resumed) {
      _initialize();
    }
  }

  Future<void> _initialize() async {
    if (mounted) {
      setState(() {
        _initializing = true;
        _error = null;
      });
    }

    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        throw CameraException(
          'no_cameras',
          'No se encontró ninguna cámara en este dispositivo.',
        );
      }

      final selected = _selectCamera(cameras);
      final controller = CameraController(
        selected,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid
            ? ImageFormatGroup.yuv420
            : ImageFormatGroup.bgra8888,
      );
      await controller.initialize();

      if (!mounted) {
        await controller.dispose();
        return;
      }

      _controller = controller;
      setState(() => _initializing = false);
      await _startStream();
    } on CameraException catch (error) {
      if (!mounted) return;
      setState(() {
        _initializing = false;
        _error = _describeCameraError(error);
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _initializing = false;
        _error = 'No se pudo iniciar la cámara: $error';
      });
    }
  }

  CameraDescription _selectCamera(List<CameraDescription> cameras) {
    if (widget.useFrontCamera) {
      for (final camera in cameras) {
        if (camera.lensDirection == CameraLensDirection.front) return camera;
      }
    }
    return cameras.first;
  }

  String _describeCameraError(CameraException error) {
    switch (error.code) {
      case 'CameraAccessDenied':
      case 'CameraAccessDeniedWithoutPrompt':
        return 'Permiso de cámara denegado. Actívalo en los ajustes del '
            'sistema o elige una foto de la galería.';
      case 'CameraAccessRestricted':
        return 'El acceso a la cámara está restringido en este dispositivo.';
      default:
        return error.description ??
            'No se pudo abrir la cámara (${error.code}).';
    }
  }

  Future<void> _startStream() async {
    final controller = _controller;
    if (controller == null || _streaming || !controller.value.isInitialized) {
      return;
    }

    try {
      await controller.startImageStream((image) {
        final now = DateTime.now();
        if (now.difference(_lastMeterUpdate).inMilliseconds < 220) return;
        _lastMeterUpdate = now;
        final value = measureLuminance(image);
        if (!mounted) return;
        setState(() => _luminance = value);
      });
      _streaming = true;
    } on CameraException {
      // Some devices refuse the stream; the camera still works for stills.
    }
  }

  Future<void> _stopStream() async {
    final controller = _controller;
    if (controller == null || !_streaming) return;
    _streaming = false;
    try {
      await controller.stopImageStream();
    } on CameraException {
      // Ignore: stopping a stream that never started is harmless.
    }
  }

  Future<void> _disposeCamera() async {
    _streaming = false;

    final controller = _controller;
    _controller = null;
    await controller?.dispose();
  }

  Future<void> _capture() async {
    final controller = _controller;
    if (controller == null || !controller.value.isInitialized || _busy) return;

    setState(() => _takingPicture = true);
    try {
      await _stopStream();
      final shot = await controller.takePicture();
      final bytes = await shot.readAsBytes();
      if (!mounted) return;
      widget.onImageCaptured(bytes);
    } on CameraException catch (error) {
      if (!mounted) return;
      setState(
        () => _error = 'No se pudo tomar la foto. ${error.description ?? ''}',
      );
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = 'No se pudo tomar la foto: $error');
    } finally {
      if (mounted) {
        setState(() => _takingPicture = false);
        await _startStream();
      }
    }
  }

  Future<void> _pickFromGallery() async {
    if (_busy) return;
    final picked = await ImagePicker().pickImage(
      source: ImageSource.gallery,
      imageQuality: 88,
    );
    if (picked == null) return;
    final bytes = await picked.readAsBytes();
    if (!mounted) return;
    widget.onImageCaptured(bytes);
  }

  @override
  Widget build(BuildContext context) {
    if (_initializing) {
      return const _CameraPlaceholder(
        icon: Icons.camera_alt_outlined,
        title: 'Preparando la cámara…',
        showSpinner: true,
      );
    }

    final controller = _controller;
    if (controller == null || !controller.value.isInitialized) {
      return _CameraPlaceholder(
        icon: Icons.no_photography_outlined,
        title: 'Cámara no disponible',
        message: _error ?? 'No se pudo iniciar la cámara.',
        action: FilledButton.icon(
          onPressed: _pickFromGallery,
          icon: const Icon(Icons.photo_library_outlined),
          label: const Text('Elegir foto de la galería'),
        ),
      );
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(
          color: Colors.black,
          child: FittedBox(
            fit: BoxFit.cover,
            child: SizedBox(
              width: controller.value.previewSize?.height ?? 720,
              height: controller.value.previewSize?.width ?? 1280,
              child: CameraPreview(controller),
            ),
          ),
        ),
        if (widget.showOval)
          Positioned.fill(child: CustomPaint(painter: _OvalScrimPainter())),
        Positioned(
          left: 16,
          right: 16,
          bottom: 0,
          child: SafeArea(
            top: false,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _LightMeter(value: _luminance),
                const SizedBox(height: 10),
                Text(
                  widget.hint,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  _InlineNotice(message: _error!),
                ],
                const SizedBox(height: 14),
                _CaptureControls(
                  busy: _busy,
                  onCapture: _capture,
                  onGallery: _pickFromGallery,
                ),
                const SizedBox(height: 18),
              ],
            ),
          ),
        ),
        if (_busy)
          const Positioned.fill(
            child: ColoredBox(
              color: Color(0x66000000),
              child: Center(
                child: CircularProgressIndicator(color: Colors.white),
              ),
            ),
          ),
      ],
    );
  }
}

class _CaptureControls extends StatelessWidget {
  const _CaptureControls({
    required this.busy,
    required this.onCapture,
    required this.onGallery,
  });

  final bool busy;
  final VoidCallback onCapture;
  final VoidCallback onGallery;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        IconButton.filledTonal(
          onPressed: busy ? null : onGallery,
          tooltip: 'Elegir de la galería',
          icon: const Icon(Icons.photo_library_outlined),
        ),
        GestureDetector(
          onTap: busy ? null : onCapture,
          child: Container(
            width: 74,
            height: 74,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 4),
              color: Colors.white24,
            ),
            padding: const EdgeInsets.all(6),
            child: Container(
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white,
              ),
              child: const Icon(Icons.camera_alt, color: Colors.black87),
            ),
          ),
        ),
        const SizedBox(width: 48),
      ],
    );
  }
}

class _LightMeter extends StatelessWidget {
  const _LightMeter({required this.value});

  final double? value;

  @override
  Widget build(BuildContext context) {
    final level = value;
    if (level == null) {
      return const _Pill(
        icon: Icons.wb_sunny_outlined,
        text: 'Midiendo la luz…',
        color: Colors.white70,
      );
    }

    late final String label;
    late final Color color;
    if (level < 30) {
      label = 'Poca luz: busca una ventana o enciende una lámpara';
      color = const Color(0xFFFFB74D);
    } else if (level > 88) {
      label = 'Luz muy fuerte: evita el contraluz directo';
      color = const Color(0xFFFF8A65);
    } else {
      label = 'Buena iluminación (${level.round()}%)';
      color = const Color(0xFF81C784);
    }

    return _Pill(icon: Icons.wb_sunny_outlined, text: label, color: color);
  }
}

class _Pill extends StatelessWidget {
  const _Pill({required this.icon, required this.text, required this.color});

  final IconData icon;
  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Flexible(
            child: Text(text, style: TextStyle(color: color, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

class _InlineNotice extends StatelessWidget {
  const _InlineNotice({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.redAccent.withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        message,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}

class _CameraPlaceholder extends StatelessWidget {
  const _CameraPlaceholder({
    required this.icon,
    required this.title,
    this.message,
    this.action,
    this.showSpinner = false,
  });

  final IconData icon;
  final String title;
  final String? message;
  final Widget? action;
  final bool showSpinner;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: Colors.black,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (showSpinner)
                const CircularProgressIndicator(color: Colors.white)
              else
                Icon(icon, color: Colors.white70, size: 48),
              const SizedBox(height: 16),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (message != null) ...[
                const SizedBox(height: 8),
                Text(
                  message!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
              if (action != null) ...[const SizedBox(height: 20), action!],
            ],
          ),
        ),
      ),
    );
  }
}

/// Dims everything except the oval, so the face is easy to frame.
class _OvalScrimPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final bounds = Offset.zero & size;
    final oval = Rect.fromCenter(
      center: Offset(size.width / 2, size.height * 0.42),
      width: size.width * 0.74,
      height: size.height * 0.52,
    );

    final scrim = Path.combine(
      PathOperation.difference,
      Path()..addRect(bounds),
      Path()..addOval(oval),
    );

    canvas.drawPath(
      scrim,
      Paint()..color = Colors.black.withValues(alpha: 0.5),
    );
    canvas.drawOval(
      oval,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..color = Colors.white.withValues(alpha: 0.75),
    );
  }

  @override
  bool shouldRepaint(covariant _OvalScrimPainter oldDelegate) => false;
}
