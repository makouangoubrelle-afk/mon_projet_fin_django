import 'package:flutter_test/flutter_test.dart';

import 'package:sih_mobile/main.dart';

void main() {
  testWidgets('App démarre sur l\'écran de connexion', (tester) async {
    await tester.pumpWidget(const SghlMobileApp());
    expect(find.text('SGHL Mobile'), findsOneWidget);
    expect(find.text('Connexion patient'), findsOneWidget);
  });
}
