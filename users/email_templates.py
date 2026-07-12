"""Templates HTML pour les emails OTP SGHL."""


def format_otp_code(code: str) -> str:
    digits = ''.join(c for c in (code or '') if c.isdigit())[:6]
    return ' '.join(digits)


def build_otp_email_html(
    *,
    code: str,
    username: str,
    role_label: str,
    role_code: str,
    display_name: str,
    validity_minutes: int,
    app_name: str = 'SGHL ERP MÉDICAL',
    hospital_name: str = 'CHU — Centre Hospitalier Universitaire',
) -> str:
    code_spaced = format_otp_code(code)
    greeting = display_name or username or 'Utilisateur'

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code de connexion</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:Segoe UI,Roboto,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0f172a;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:420px;background:#111827;border-radius:20px;overflow:hidden;border:1px solid #1f2937;">
          <tr>
            <td style="padding:28px 24px 20px;background:linear-gradient(135deg,#0ea5e9 0%,#14b8a6 100%);">
              <p style="margin:0 0 6px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.85);">{app_name}</p>
              <h1 style="margin:0;font-size:28px;line-height:1.2;color:#ffffff;font-weight:700;">Code de vérification</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:28px 24px 8px;color:#e2e8f0;">
              <p style="margin:0 0 12px;font-size:16px;color:#ffffff;">Bonjour {greeting},</p>
              <p style="margin:0;font-size:14px;line-height:1.6;color:#94a3b8;">
                Comme pour lier WhatsApp à un nouvel appareil : saisissez ce code à 6 chiffres pour confirmer votre connexion.
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:20px 24px 8px;">
              <div style="font-size:42px;font-weight:700;letter-spacing:0.35em;color:#2dd4bf;font-family:Consolas,Monaco,monospace;">
                {code_spaced}
              </div>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:0 24px 24px;">
              <p style="margin:0;font-size:13px;color:#64748b;">Ce code expire dans {validity_minutes} minutes.</p>
            </td>
          </tr>
          <tr>
            <td style="padding:0 24px 24px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0b1220;border:1px solid #1e293b;border-radius:14px;">
                <tr>
                  <td style="padding:14px 16px;border-bottom:1px solid #1e293b;">
                    <span style="font-size:12px;color:#64748b;">Compte</span><br>
                    <strong style="font-size:15px;color:#ffffff;">{username}</strong>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 16px;">
                    <span style="font-size:12px;color:#64748b;">Rôle</span><br>
                    <strong style="font-size:15px;color:#ffffff;">{role_code}</strong>
                    <span style="font-size:12px;color:#94a3b8;"> · {role_label}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:0 24px 28px;">
              <p style="margin:0;font-size:11px;line-height:1.5;color:#475569;text-align:center;">
                {hospital_name}<br>
                Données chiffrées · Conformité RGPD
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def build_otp_email_text(
    *,
    code: str,
    username: str,
    role_label: str,
    role_code: str,
    display_name: str,
    validity_minutes: int,
) -> str:
    greeting = display_name or username or 'Utilisateur'
    return (
        f'Bonjour {greeting},\n\n'
        f'Code de vérification SGHL (comme WhatsApp)\n\n'
        f'Entrez ce code dans l\'application pour vous connecter :\n\n'
        f'{code}\n\n'
        f'Compte : {username}\n'
        f'Rôle : {role_code} ({role_label})\n\n'
        f'Ce code expire dans {validity_minutes} minutes.\n'
        f"Ne partagez ce code avec personne.\n"
    )
