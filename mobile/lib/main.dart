import 'package:flutter/material.dart';
import 'services/asesor_api.dart';
import 'theme/app_theme.dart';
import 'views/android_demo.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(AsesorIaApp());
}

class AsesorIaApp extends StatefulWidget {
  AsesorIaApp({super.key, AsesorApi? api}) : api = api ?? AsesorApi();
  final AsesorApi api;
  @override
  State<AsesorIaApp> createState() => _AsesorIaAppState();
}

class _AsesorIaAppState extends State<AsesorIaApp> {
  int session = 0;
  @override
  void initState() {
    super.initState();
    widget.api.onUnauthorized = () {
      if (mounted) {
        setState(() {
          session++;
        });
      }
    };
  }

  @override
  void dispose() {
    widget.api.onUnauthorized = null;
    super.dispose();
  }

  void refreshSession() => setState(() {
    session++;
  });
  @override
  Widget build(BuildContext context) => MaterialApp(
    key: ValueKey(session),
    title: 'Facial y Moda',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.light(),
    home: widget.api.token == null
        ? AuthPage(
            key: ValueKey('auth-$session'),
            api: widget.api,
            onLogin: refreshSession,
          )
        : DemoHomePage(
            key: ValueKey('home-$session'),
            api: widget.api,
            onLogout: () {
              widget.api.logout();
              refreshSession();
            },
          ),
  );
}
