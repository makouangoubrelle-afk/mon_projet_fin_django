import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../config/api_config.dart';
import '../services/api_client.dart';
import 'login_screen.dart';

class StaffRedirectScreen extends StatelessWidget {
  const StaffRedirectScreen({
    super.key,
    required this.client,
    required this.roleLabel,
    required this.email,
  });

  final ApiClient client;
  final String roleLabel;
  final String email;

  String get _webUrl {
    if (ApiConfig.origin.isNotEmpty) return ApiConfig.origin;
    if (kIsWeb) return Uri.base.origin;
    return 'https://mon-projet-fin-django.onrender.com';
  }

  Future<void> _openWebApp() async {
    final uri = Uri.parse(_webUrl);
    if (kIsWeb) {
      await launchUrl(uri, webOnlyWindowName: '_self');
      return;
    }
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }

  void _logout(BuildContext context) {
    client
      ..token = null
      ..patientId = null
      ..patientNom = null;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => LoginScreen(client: client)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SGHL Mobile'),
        actions: [
          IconButton(
            onPressed: () => _logout(context),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.admin_panel_settings_outlined, size: 64, color: Color(0xFF2DD4BF)),
            const SizedBox(height: 24),
            Text(
              'Compte $roleLabel',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            Text(
              'L\'application mobile est réservée aux patients.\n'
              'Votre email ($email) est un compte personnel hospitalier.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade400, height: 1.5),
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: _openWebApp,
              icon: const Icon(Icons.open_in_browser),
              label: const Text('Ouvrir l\'interface complète'),
            ),
            const SizedBox(height: 12),
            Text(
              'Pour tester l\'espace patient, connectez-vous avec\npatient@gmail.com',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade500, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
}
