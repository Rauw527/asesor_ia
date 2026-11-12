import 'dart:io';
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Local persistence for the comparison photos.
///
/// The monthly flow needs the *same* Day 1 photo a month later, so the baseline
/// is copied into the app documents directory instead of relying on a photo
/// picker path that may disappear.
class PhotoStore {
  static const _baselinePathKey = 'baseline_photo_path';
  static const _baselineDateKey = 'baseline_photo_date';

  Future<String> saveBaseline(Uint8List bytes) async {
    final directory = await getApplicationDocumentsDirectory();
    final file = File(
      '${directory.path}/baseline_${DateTime.now().millisecondsSinceEpoch}.jpg',
    );
    await file.writeAsBytes(bytes, flush: true);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_baselinePathKey, file.path);
    await prefs.setString(_baselineDateKey, DateTime.now().toIso8601String());
    return file.path;
  }

  Future<File?> baselineFile() async {
    final prefs = await SharedPreferences.getInstance();
    final path = prefs.getString(_baselinePathKey);
    if (path == null) return null;
    final file = File(path);
    return await file.exists() ? file : null;
  }

  Future<DateTime?> baselineDate() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_baselineDateKey);
    return raw == null ? null : DateTime.tryParse(raw);
  }

  Future<int?> daysSinceBaseline() async {
    final date = await baselineDate();
    if (date == null) return null;
    return DateTime.now().difference(date).inDays;
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    final path = prefs.getString(_baselinePathKey);
    if (path != null) {
      final file = File(path);
      if (await file.exists()) await file.delete();
    }
    await prefs.remove(_baselinePathKey);
    await prefs.remove(_baselineDateKey);
  }
}

/// Mean luminance (0-100) of a camera frame, used by the light calibrator.
///
/// YUV420 exposes luma in the first plane; BGRA (iOS) needs a weighted mix.
double measureLuminance(CameraImage image) {
  if (image.planes.isEmpty) return 0;

  final plane = image.planes.first;
  final bytes = plane.bytes;
  if (bytes.isEmpty) return 0;

  if (image.format.group == ImageFormatGroup.bgra8888) {
    var sum = 0.0;
    var samples = 0;
    for (var i = 0; i + 2 < bytes.length; i += 4 * 8) {
      final b = bytes[i];
      final g = bytes[i + 1];
      final r = bytes[i + 2];
      sum += 0.114 * b + 0.587 * g + 0.299 * r;
      samples++;
    }
    return samples == 0 ? 0 : (sum / samples) / 2.55;
  }

  var sum = 0;
  var samples = 0;
  for (var i = 0; i < bytes.length; i += 8) {
    sum += bytes[i];
    samples++;
  }
  return samples == 0 ? 0 : (sum / samples) / 2.55;
}
