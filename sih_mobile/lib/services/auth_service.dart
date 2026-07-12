import 'api_client.dart';

class AuthService {
  AuthService(this._client);

  final ApiClient _client;

  Future<Map<String, dynamic>> lookup(String email) {
    final q = Uri(queryParameters: {'email': email.trim()}).query;
    return _client.getJson('/auth/lookup?$q');
  }

  Future<Map<String, dynamic>> sendCode(String email, {String role = ''}) {
    return _client.postJson('/auth/send-code', {
      'email': email.trim(),
      if (role.isNotEmpty) 'role': role,
      'channel': 'email',
    });
  }

  Future<Map<String, dynamic>> verifyCode(
    String email,
    String code, {
    String role = '',
  }) {
    return _client.postJson('/auth/verify-code', {
      'email': email.trim(),
      'code': code.trim(),
      if (role.isNotEmpty) 'role': role,
    });
  }
}
