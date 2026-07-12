import 'api_client.dart';

class PatientService {
  PatientService(this._client);

  final ApiClient _client;

  Future<Map<String, dynamic>> fetchDossier(int patientId) {
    return _client.getJson('/reception/patients/$patientId/dossier');
  }

  Future<Map<String, dynamic>> fetchMyDossier(String email) {
    final q = Uri(queryParameters: {'email': email.trim()}).query;
    return _client.getJson('/reception/mon-dossier?$q');
  }
}
