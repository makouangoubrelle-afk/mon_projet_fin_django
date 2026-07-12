import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../services/patient_service.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.client,
    required this.userName,
    required this.roleLabel,
  });

  final ApiClient client;
  final String userName;
  final String roleLabel;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final PatientService _patients = PatientService(widget.client);

  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _dossier;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final id = widget.client.patientId;
    if (id == null) {
      setState(() {
        _loading = false;
        _error = 'Aucun dossier patient lié à ce compte.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await _patients.fetchDossier(id);
      final profil = data['profil'] as Map<String, dynamic>?;
      if (profil != null) {
        final nom = '${profil['nom'] ?? ''} ${profil['prenom'] ?? ''}'.trim();
        if (nom.isNotEmpty) widget.client.patientNom = nom;
      }
      setState(() => _dossier = data);
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _loading = false);
    }
  }

  void _logout() {
    widget.client
      ..token = null
      ..patientId = null
      ..patientNom = null;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => LoginScreen(client: widget.client)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final profil = _dossier?['profil'] as Map<String, dynamic>?;
    final ordonnances = (_dossier?['ordonnances'] as List?) ?? [];
    final analyses = (_dossier?['analyses'] as List?) ?? [];
    final loc = _dossier?['localisation'] as Map<String, dynamic>?;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon espace SGHL'),
        actions: [
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_error != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text(_error!, style: const TextStyle(color: Colors.redAccent)),
                      const SizedBox(height: 12),
                      OutlinedButton(onPressed: _load, child: const Text('Réessayer')),
                    ],
                  ),
                ),
              )
            else if (profil != null) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${profil['nom'] ?? ''} ${profil['prenom'] ?? ''}'.trim(),
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      Text('${widget.roleLabel} · ${widget.userName}'),
                      if (profil['telephone'] != null)
                        Text('Tél. ${profil['telephone']}'),
                      if (profil['groupe_sanguin'] != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Chip(
                            label: Text('Groupe ${profil['groupe_sanguin']}'),
                            backgroundColor: Colors.red.withValues(alpha: 0.15),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              if (loc != null) ...[
                const SizedBox(height: 12),
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.location_on_outlined, color: Color(0xFF2DD4BF)),
                    title: const Text('Localisation'),
                    subtitle: Text(
                      '${loc['batiment'] ?? '—'} · ${loc['salle'] ?? '—'}\n'
                      '${loc['service_nom'] ?? ''}',
                    ),
                    isThreeLine: true,
                  ),
                ),
              ],
              const SizedBox(height: 12),
              _SectionTitle('Ordonnances (${ordonnances.length})'),
              if (ordonnances.isEmpty)
                const _EmptyHint('Aucune ordonnance.')
              else
                ...ordonnances.take(5).map((o) {
                  final item = o as Map<String, dynamic>;
                  return Card(
                    child: ListTile(
                      title: Text(item['medicaments']?.toString() ?? '—'),
                      subtitle: Text(item['date_ordonnance']?.toString() ?? ''),
                      isThreeLine: true,
                    ),
                  );
                }),
              const SizedBox(height: 12),
              _SectionTitle('Analyses (${analyses.length})'),
              if (analyses.isEmpty)
                const _EmptyHint('Aucune analyse.')
              else
                ...analyses.take(5).map((a) {
                  final item = a as Map<String, dynamic>;
                  return Card(
                    child: ListTile(
                      title: Text(item['examen_nom']?.toString() ?? '—'),
                      subtitle: Text(item['statut']?.toString() ?? ''),
                      trailing: item['resultat'] != null
                          ? const Icon(Icons.check_circle_outline, color: Colors.green)
                          : null,
                    ),
                  );
                }),
            ],
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Text(text, style: Theme.of(context).textTheme.titleMedium),
    );
  }
}

class _EmptyHint extends StatelessWidget {
  const _EmptyHint(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(text, style: TextStyle(color: Colors.grey.shade500)),
    );
  }
}
