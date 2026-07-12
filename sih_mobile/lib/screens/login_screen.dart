import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/api_client.dart';
import '../services/auth_service.dart';
import 'home_screen.dart';
import 'staff_redirect_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.client});

  final ApiClient client;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _codeCtrl = TextEditingController();
  late final AuthService _auth = AuthService(widget.client);

  bool _codeStep = false;
  bool _loading = false;
  String? _error;
  String? _info;
  String? _debugCode;
  String _emailSent = '';

  @override
  void dispose() {
    _emailCtrl.dispose();
    _codeCtrl.dispose();
    super.dispose();
  }

  Future<void> _sendCode() async {
    final email = _emailCtrl.text.trim();
    if (email.isEmpty) {
      setState(() => _error = 'Entrez votre adresse email.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _info = null;
    });

    try {
      final lookup = await _auth.lookup(email);
      final roleLabel = lookup['role_label']?.toString() ?? '';
      if (lookup['found'] == true &&
          roleLabel.isNotEmpty &&
          !roleLabel.toLowerCase().contains('patient')) {
        setState(() {
          _info =
              'Compte $roleLabel détecté. Cette app est pour les patients — '
              'vous serez redirigé vers l\'interface web après connexion.';
        });
      }

      final res = await _auth.sendCode(email);
      if (res['success'] != true) {
        throw Exception(res['detail']?.toString() ?? 'Envoi impossible');
      }
      setState(() {
        _codeStep = true;
        _emailSent = res['email']?.toString() ?? email;
        _info = res['detail']?.toString();
        _debugCode = res['debug_code']?.toString();
      });
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _verify() async {
    final code = _codeCtrl.text.replaceAll(RegExp(r'\D'), '');
    if (code.length != 6) {
      setState(() => _error = 'Le code doit contenir 6 chiffres.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final res = await _auth.verifyCode(_emailSent, code);
      if (res['success'] != true) {
        throw Exception(res['detail']?.toString() ?? 'Code refusé');
      }

      widget.client.token = res['token']?.toString();
      final patientId = res['patient_id'];
      if (patientId is int) {
        widget.client.patientId = patientId;
      } else if (patientId != null) {
        widget.client.patientId = int.tryParse('$patientId');
      }

      final role = res['role']?.toString() ?? 'PATIENT';
      final roleLabel = res['role_label']?.toString() ?? 'Patient';
      final userEmail = res['email']?.toString() ?? _emailSent;

      if (!mounted) return;

      if (role != 'PATIENT') {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => StaffRedirectScreen(
              client: widget.client,
              roleLabel: roleLabel,
              email: userEmail,
            ),
          ),
        );
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomeScreen(
            client: widget.client,
            userName: res['username']?.toString() ?? userEmail,
            roleLabel: roleLabel,
            userEmail: userEmail,
          ),
        ),
      );
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  void _fillDebugCode() {
    if (_debugCode != null && _debugCode!.length == 6) {
      _codeCtrl.text = _debugCode!;
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'SGHL Mobile',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2DD4BF),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _codeStep ? 'Vérification OTP' : 'Connexion patient',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey.shade400),
                  ),
                  if (!_codeStep)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Utilisez votre email patient (ex. patient@gmail.com)',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                      ),
                    ),
                  const SizedBox(height: 32),
                  if (!_codeStep) ...[
                    TextField(
                      controller: _emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      autocorrect: false,
                      decoration: const InputDecoration(
                        labelText: 'Email patient',
                        hintText: 'patient@gmail.com',
                        prefixIcon: Icon(Icons.mail_outline),
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: _loading ? null : _sendCode,
                      child: _loading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Recevoir le code'),
                    ),
                  ] else ...[
                    Text(
                      'Code envoyé à $_emailSent',
                      style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    if (_debugCode != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        margin: const EdgeInsets.only(bottom: 16),
                        decoration: BoxDecoration(
                          color: Colors.amber.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.amber.withValues(alpha: 0.4)),
                        ),
                        child: Column(
                          children: [
                            Text(
                              _debugCode!,
                              style: const TextStyle(
                                fontSize: 28,
                                letterSpacing: 8,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            TextButton(
                              onPressed: _fillDebugCode,
                              child: const Text('Remplir automatiquement'),
                            ),
                          ],
                        ),
                      ),
                    TextField(
                      controller: _codeCtrl,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 24, letterSpacing: 12),
                      decoration: const InputDecoration(
                        labelText: 'Code à 6 chiffres',
                        counterText: '',
                      ),
                      onSubmitted: (_) => _verify(),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: _loading ? null : _verify,
                      child: _loading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Se connecter'),
                    ),
                    TextButton(
                      onPressed: _loading
                          ? null
                          : () => setState(() {
                                _codeStep = false;
                                _codeCtrl.clear();
                                _debugCode = null;
                              }),
                      child: const Text('Changer d\'email'),
                    ),
                  ],
                  if (_info != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _info!,
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.teal.shade200, fontSize: 13),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _error!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.redAccent),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
