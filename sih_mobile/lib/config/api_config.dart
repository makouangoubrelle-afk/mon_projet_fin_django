/// URL de l'API SGHL.
/// - Web hébergé sur Render : chemin relatif `/api`
/// - APK / iOS : URL complète via `--dart-define=API_BASE=https://...`
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE',
    defaultValue: '/api',
  );

  static String get origin {
    if (baseUrl.startsWith('http')) {
      final uri = Uri.parse(baseUrl);
      return '${uri.scheme}://${uri.host}${uri.hasPort ? ':${uri.port}' : ''}';
    }
    return '';
  }
}
