import 'dart:typed_data';

import 'package:flutter/material.dart';

/// Draggable reveal slider used for the Day 1 vs. today comparison.
class BeforeAfterSlider extends StatefulWidget {
  const BeforeAfterSlider({
    super.key,
    required this.before,
    required this.after,
    this.beforeLabel = 'Día 1',
    this.afterLabel = 'Hoy',
    this.height = 340,
  });

  final Uint8List before;
  final Uint8List after;
  final String beforeLabel;
  final String afterLabel;
  final double height;

  @override
  State<BeforeAfterSlider> createState() => _BeforeAfterSliderState();
}

class _BeforeAfterSliderState extends State<BeforeAfterSlider> {
  double _position = 0.5;

  void _moveTo(double dx, double width) {
    if (width <= 0) return;
    setState(() => _position = (dx / width).clamp(0.02, 0.98).toDouble());
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: SizedBox(
        height: widget.height,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final width = constraints.maxWidth;
            return GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTapDown: (details) =>
                  _moveTo(details.localPosition.dx, width),
              onHorizontalDragStart: (details) =>
                  _moveTo(details.localPosition.dx, width),
              onHorizontalDragUpdate: (details) =>
                  _moveTo(details.localPosition.dx, width),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Image.memory(
                    widget.before,
                    fit: BoxFit.cover,
                    gaplessPlayback: true,
                  ),
                  ClipPath(
                    clipper: _RevealClipper(_position),
                    child: Image.memory(
                      widget.after,
                      fit: BoxFit.cover,
                      gaplessPlayback: true,
                    ),
                  ),
                  Positioned(
                    left: width * _position - 1,
                    top: 0,
                    bottom: 0,
                    child: Container(width: 2, color: Colors.white),
                  ),
                  Positioned(
                    left: width * _position - 20,
                    top: widget.height / 2 - 20,
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.white,
                        boxShadow: const [
                          BoxShadow(color: Colors.black26, blurRadius: 6),
                        ],
                      ),
                      child: const Icon(
                        Icons.unfold_more,
                        size: 20,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                  Positioned(
                    left: 12,
                    top: 12,
                    child: _SliderLabel(text: widget.beforeLabel),
                  ),
                  Positioned(
                    right: 12,
                    top: 12,
                    child: _SliderLabel(text: widget.afterLabel),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _SliderLabel extends StatelessWidget {
  const _SliderLabel({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _RevealClipper extends CustomClipper<Path> {
  _RevealClipper(this.position);

  final double position;

  @override
  Path getClip(Size size) {
    return Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width * position, size.height));
  }

  @override
  bool shouldReclip(covariant _RevealClipper oldClipper) =>
      oldClipper.position != position;
}
