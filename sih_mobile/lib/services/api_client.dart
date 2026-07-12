import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';

class ApiException implements Exception {
  ApiException(this.message);
  final String message;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({this.token, this.patientId, this.patientNom});

  String? token;
  int? patientId;
  String? patientNom;

  Map<String, String> get _headers {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null && token!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    if (patientId != null) {
      headers['X-SGHL-Patient-Id'] = '$patientId';
    }
    if (patientNom != null && patientNom!.isNotEmpty) {
      headers['X-SGHL-Patient-Nom'] = patientNom!;
    }
    return headers;
  }

  Uri _uri(String path) {
    final base = ApiConfig.baseUrl.endsWith('/')
        ? ApiConfig.baseUrl.substring(0, ApiConfig.baseUrl.length - 1)
        : ApiConfig.baseUrl;
    final clean = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$base$clean');
  }

  Future<Map<String, dynamic>> getJson(String path) async {
    final response = await http.get(_uri(path), headers: _headers);
    return _decodeMap(response);
  }

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final response = await http.post(
      _uri(path),
      headers: _headers,
      body: jsonEncode(body),
    );
    return _decodeMap(response);
  }

  Map<String, dynamic> _decodeMap(http.Response response) {
    Map<String, dynamic>? data;
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) data = decoded;
    } catch (_) {
      data = null;
    }

    if (response.statusCode >= 400) {
      final detail = data?['detail']?.toString() ??
          'Erreur ${response.statusCode}';
      throw ApiException(detail);
    }

    if (data == null) {
      throw ApiException('Réponse serveur invalide');
    }
    return data;
  }
}
