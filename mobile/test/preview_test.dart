import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/services.dart';
import 'package:asesor_ia/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'widget_test.dart' show FakeApi;

void main() {
  final output = Platform.environment['DEMO_PREVIEW_DIR'];
  testWidgets('renders Android demo previews at phone size', (tester) async {
    final fontPath = Platform.environment['DEMO_FONT_PATH'];
    if (output != null && fontPath != null) {
      await tester.runAsync(() async {
        final font = FontLoader('Roboto')
          ..addFont(
            Future.value(
              ByteData.sublistView(await File(fontPath).readAsBytes()),
            ),
          );
        await font.load();
        final fallback = FontLoader('Ahem')
          ..addFont(
            Future.value(
              ByteData.sublistView(await File(fontPath).readAsBytes()),
            ),
          );
        await fallback.load();
        final icons = FontLoader('MaterialIcons')
          ..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'));
        await icons.load();
      });
    }
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(430, 932);
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    for (final signedIn in [false, true]) {
      final boundaryKey = GlobalKey();
      final api = FakeApi()..signedIn = signedIn;
      await tester.pumpWidget(
        RepaintBoundary(
          key: boundaryKey,
          child: AsesorIaApp(api: api),
        ),
      );
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      if (output != null) {
        final boundary = tester.renderObject<RenderRepaintBoundary>(
          find.byKey(boundaryKey),
        );
        await tester.runAsync(() async {
          final image = await boundary.toImage(pixelRatio: 2);
          final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
          await File(
            '$output/${signedIn ? 'android-inicio' : 'android-acceso'}.png',
          ).writeAsBytes(bytes!.buffer.asUint8List());
          image.dispose();
        });
      }
      await tester.pumpWidget(const SizedBox());
    }
  });
}
