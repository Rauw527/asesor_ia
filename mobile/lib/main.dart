import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'controllers/inci_controller.dart';
import 'controllers/progress_controller.dart';
import 'controllers/routine_controller.dart';
import 'controllers/skin_controller.dart';
import 'controllers/user_controller.dart';
import 'services/asesor_api.dart';
import 'services/photo_store.dart';
import 'theme/app_theme.dart';
import 'views/home_page.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(AsesorIaApp(api: AsesorApi()));
}

class AsesorIaApp extends StatelessWidget {
  AsesorIaApp({super.key, AsesorApi? api}) : api = api ?? AsesorApi();

  /// Injectable for widget tests; the default talks to the real FastAPI server.
  final AsesorApi api;

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<AsesorApi>.value(value: api),
        ChangeNotifierProvider(create: (_) => UserController(api)),
        ChangeNotifierProvider(create: (_) => SkinController(api)),
        ChangeNotifierProvider(
          create: (_) => ProgressController(api, PhotoStore()),
        ),
        ChangeNotifierProvider(create: (_) => InciController(api)),
        ChangeNotifierProvider(create: (_) => RoutineController(api)),
      ],
      child: MaterialApp(
        title: 'Asesor IA',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(),
        home: const HomePage(),
      ),
    );
  }
}
