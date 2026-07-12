import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'services/api_client.dart';

void main() {
  runApp(const SghlMobileApp());
}

class SghlMobileApp extends StatelessWidget {
  const SghlMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    final client = ApiClient();
    return MaterialApp(
      title: 'SGHL Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF14B8A6),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF1E293B),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      home: LoginScreen(client: client),
    );
  }
}
