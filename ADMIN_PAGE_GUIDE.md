# Guide d'Utilisation - Page Administration

## 🎯 Accès à la Page Administration

La page administrateur est accessible via:
- **URL directe**: `/admin`
- **Route**: Configurée dans `config/navigation.js`
- **Rôles autorisés**: `ADMIN` uniquement

### Dans le menu principal:
```
⚙️ Administration → Panneau d'Administration
```

---

## 📖 Guide Complet des 4 Onglets

### 1. 👤 Onglet "Utilisateurs"

#### Vue d'ensemble:
- Liste de tous les utilisateurs du système
- Filtrage par rôle
- Gestion des statuts (actif/inactif)

#### Actions disponibles:

**Créer un nouvel utilisateur**:
1. Cliquez sur bouton "➕ Nouvel utilisateur"
2. Remplissez le formulaire:
   - 📧 Email: `utilisateur@hospital.com`
   - 🎭 Rôle: Sélectionnez dans la liste
   - 📱 Téléphone: (optionnel)
3. Cliquez "✓ Créer"

**Éditer un utilisateur**:
1. Cliquez sur "✏️ Éditer" dans la ligne
2. Modifiez les informations
3. Cliquez "✓ Enregistrer"

**Supprimer un utilisateur**:
1. Cliquez sur "🗑️ Supprimer"
2. Confirmez la suppression
3. L'utilisateur est supprimé de la liste

**Activer/Désactiver un utilisateur**:
- Bouton dans la colonne "Actions"
- Bascule instantanée du statut
- Les utilisateurs inactifs ne peuvent pas se connecter

#### Filtrage:
- Cliquez sur le badge d'un rôle pour filtrer
- "✓ Tous" pour afficher tous les utilisateurs
- Le tableau se rafraîchit automatiquement

---

### 2. 🎭 Onglet "Rôles"

#### Vue d'ensemble:
- Vue en grille des rôles disponibles
- Nombre d'utilisateurs par rôle
- Icônes représatives

#### Rôles disponibles:

| Icône | Rôle | Description |
|-------|------|-------------|
| 👨‍💼 | Administrateur | Accès complet au système |
| 👨‍⚕️ | Médecin | Gestion consultations & prescriptions |
| 💉 | Infirmier | Suivi patients & soins |
| 🏪 | Réceptionniste | Accueil & rendez-vous |
| 💊 | Pharmacien | Gestion médicaments |

#### Actions par rôle:

**Éditer un rôle**:
1. Cliquez "✏️ Éditer" sur la carte du rôle
2. Modifiez:
   - Nom
   - Description
   - Permissions (voir onglet Permissions)
3. Cliquez "✓ Enregistrer"

**Supprimer un rôle**:
1. Cliquez "🗑️ Supprimer"
2. Confirmez l'action
3. ⚠️ Les utilisateurs du rôle seront reassignés

**Créer un rôle**:
1. Cliquez "➕ Nouveau rôle"
2. Définissez:
   - Nom du rôle
   - Description
   - Icône
   - Permissions
3. Cliquez "✓ Créer"

---

### 3. 🔑 Onglet "Permissions"

#### Vue d'ensemble:
- Matrice interactive rôle × permission
- Permet d'attribuer finement les droits
- Scroll horizontal sur larges écrans

#### Permissions disponibles:

**Gestion utilisateurs**:
- Créer utilisateurs
- Modifier utilisateurs
- Supprimer utilisateurs

**Gestion patients**:
- Voir patients
- Modifier patients

**Gestion consultations**:
- Voir consultations
- Créer consultations

**Gestion facturation**:
- Voir facturation
- Créer factures

**Rapports**:
- Voir rapports

#### Comment utiliser:

1. **Trouver la permission** dans la première colonne
2. **Naviguer horizontalement** vers le rôle souhaité
3. **Cocher/décocher** la case pour activer/désactiver
4. Les modifications sont **automatiquement sauvegardées**

#### Code couleur:
- ✅ Case cochée = Permission accordée
- ☐ Case vide = Permission refusée

#### Conseil:
> Pour les administrateurs, toutes les permissions doivent être cochées (✓ Complet)

---

### 4. 🔔 Onglet "Notifications"

#### Vue d'ensemble:
- Affichage des alertes système actives
- Gestion des préférences de notification
- Paramètres de délivrance

#### Types de notifications:

| Type | Couleur | Exemples |
|------|---------|----------|
| 🚨 Urgent | 🔴 Rouge | Nouvelle admission, Urgence critique |
| ⚠️ Warning | 🟡 Jaune | Quota disque élevé, Maintenance |
| ✅ Info | 🔵 Bleu | Sauvegarde terminée, Sync réussie |

#### Gestion des notifications actives:

**Fermer une notification**:
1. Cliquez sur "✕" dans le coin droit
2. La notification disparaît de la liste
3. Elle peut réapparaître si l'alerte persiste

**Filtrer par type**:
- Les notifications sont classées par type automatiquement
- Urgent apparaît toujours en haut

#### Paramètres de notifications:

**📧 Alertes email**:
- ☑️ Actif: Notifications envoyées par email
- ☐ Inactif: Pas de notifications email

**📱 Alertes SMS**:
- ☑️ Actif: Notifications par SMS
- ☐ Inactif: Pas de SMS

**🔔 Notifications in-app**:
- ☑️ Actif: Affichage dans l'interface
- ☐ Inactif: Pas de notifications visuelles

#### Sauvegarder les paramètres:
1. Ajustez les 3 paramètres
2. Cliquez "💾 Enregistrer les paramètres"
3. Un message de confirmation apparaît
4. Les paramètres sont persistés

---

## 🎯 Scénarios Courants

### Scenario 1: Ajouter un nouveau médecin

```
1. Onglet Utilisateurs
2. Cliquez "➕ Nouvel utilisateur"
3. Email: dr.martin@hospital.com
4. Rôle: MEDECIN
5. Téléphone: +33 1 23 45 67 89
6. Cliquez "✓ Créer"
7. Nouveau médecin créé avec accès complet
```

### Scenario 2: Désactiver un utilisateur temporaire

```
1. Onglet Utilisateurs
2. Cherchez l'utilisateur dans la liste
3. Cliquez "🔒 Désactiver"
4. L'utilisateur passe en statut "✕ Inactif"
5. Il ne peut plus se connecter
6. Cliquez "🔓 Activer" pour réactiver
```

### Scenario 3: Configurer les permissions d'un rôle

```
1. Onglet Permissions
2. Trouvez la ligne du rôle (ex: INFIRMIER)
3. Cochez les cases des permissions souhaitées:
   - Voir patients: ✓
   - Modifier patients: ☐
   - Créer consultations: ✓
   - Voir facturation: ☐
4. Les permissions sont sauvegardées automatiquement
5. Les infirmiers ont désormais ces droits
```

### Scenario 4: Ajouter un nouvel type d'alerte

```
1. Onglet Notifications
2. Cliquez "➕ Nouvelle notification"
3. Remplissez:
   - Titre: "Maintenance serveur"
   - Message: "Maintenance prévue..."
   - Type: Warning
   - Icône: ⚠️
4. Cliquez "✓ Créer"
5. L'alerte est affichée à tous les users configurés
```

---

## 🔒 Sécurité & Permissions

### Accès à l'administration:
```javascript
// Seuls les ADMIN peuvent voir la page
if (user.role !== 'ADMIN') {
  router.push('/login')
}
```

### Changements traçables:
- Chaque action est loggée
- Historique conservé (voir Journal)
- Traçabilité complète pour audit

---

## 📊 Intégration Backend

### Endpoints API attendus:

```javascript
// Utilisateurs
GET    /api/users/              // Lister
POST   /api/users/              // Créer
PUT    /api/users/{id}/         // Modifier
DELETE /api/users/{id}/         // Supprimer

// Rôles
GET    /api/roles/              // Lister
POST   /api/roles/              // Créer
PUT    /api/roles/{id}/         // Modifier
DELETE /api/roles/{id}/         // Supprimer

// Permissions
GET    /api/permissions/        // Lister
POST   /api/permissions/        // Créer
PUT    /api/permissions/{id}/   // Modifier

// Notifications
GET    /api/notifications/      // Lister
POST   /api/notifications/      // Créer
DELETE /api/notifications/{id}/ // Supprimer
```

### Format de réponse exemple:

```json
{
  "users": [
    {
      "id": 1,
      "email": "admin@hospital.com",
      "role": "ADMIN",
      "actif": true,
      "nom": "Admin",
      "prenom": "System"
    }
  ],
  "total": 5
}
```

---

## 💡 Tips & Astuces

### ⚡ Navigation rapide:
- Onglets avec Alt+U, Alt+R, Alt+P, Alt+N
- Boutons d'action toujours en même position
- Consistent avec le reste de l'app

### 🎨 Personnalisation:
- Tous les styles utilisant Tailwind CSS
- Changer les couleurs facile (modifier les variables)
- Responsive par défaut sur mobile/tablette

### 🔍 Debugging:
- Console browser: `F12` pour voir les logs
- Données en local: `localStorage` pour les paramètres
- Exemple: `localStorage.getItem('admin-notifications')`

---

## ❓ FAQ

**Q: Comment puis-je exporter la liste des utilisateurs?**  
R: Allez en Rapports → Utilisateurs → Exporter en CSV

**Q: Puis-je créer des rôles personnalisés?**  
R: Oui, cliquez "➕ Nouveau rôle" et définissez les permissions

**Q: Les modifications sont-elles sauvegardées automatiquement?**  
R: Oui pour les permissions, confirmé pour les autres actions

**Q: Comment réinitialiser les permissions?**  
R: Attendez une mise à jour du bouton "Réinitialiser par défaut"

**Q: Puis-je supprimer un rôle utilisé?**  
R: Non, vous devez d'abord reassigner les utilisateurs

---

## 📞 Support

Pour des questions ou problèmes:
1. Consultez la Documentation: `/docs`
2. Contactez l'équipe admin: `admin@hospital.com`
3. Rapportez un bug: Issues → GitHub

---

**Dernière mise à jour**: 11 juillet 2026  
**Version**: 1.0  
**Auteur**: Admin System  
**Support**: 24/7
