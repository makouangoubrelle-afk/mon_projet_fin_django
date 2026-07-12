import 'api_client.dart';

class PatientService {
  PatientService(this._client);

  final ApiClient _client;

  Future<Map<String, dynamic>> fetchDossier(int patientId) {
    return _client.getJson('/reception/patients/$patientId/dossier');
  }
}
