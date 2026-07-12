#!/usr/bin/env python3
"""Vérification rapide SGHL — backend + fichiers frontend."""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = 'http://127.0.0.1:8001'
ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / 'sih-frontend'

errors = []
warnings = []


def get(path, headers=None):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


def post(path, data, headers=None):
    h = {'Content-Type': 'application/json', **(headers or {})}
    req = urllib.request.Request(
        BASE + path, data=json.dumps(data).encode(), headers=h, method='POST',
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


def check(name, ok, detail=''):
    status = 'OK' if ok else 'FAIL'
    line = f'[{status}] {name}' + (f' — {detail}' if detail else '')
    print(line)
    if not ok:
        errors.append(line)


print('=== SGHL Verification ===\n')

# Views referenced in navigation
nav = (FRONT / 'src/config/navigation.js').read_text(encoding='utf-8')
views = re.findall(r"import\('\.\./views/([^']+)'\)", nav)
for v in views:
    check(f'Vue {v}', (FRONT / 'src/views' / v).exists())

# Public APIs
public = [
    '/api/sante', '/api/stats', '/api/auth/health', '/api/reception/patients',
    '/api/hospitalisations/admissions', '/api/caisse/factures', '/api/core/settings',
]
for p in public:
    try:
        st, _ = get(p)
        check(f'GET {p}', st == 200, str(st))
    except Exception as e:
        check(f'GET {p}', False, str(e))

# Auth OTP (DEBUG)
try:
    _, send = post('/api/auth/send-code', {'email': 'admin@sghl.com'})
    code = send.get('debug_code')
    check('OTP send-code', send.get('success') is True)
    if code:
        _, verify = post('/api/auth/verify-code', {'email': 'admin@sghl.com', 'code': code})
        check('OTP verify-code + record_login', verify.get('success') is True, verify.get('role', ''))
except Exception as e:
    check('Auth OTP', False, str(e))

# Admin protected
admin_h = {'X-SGHL-Email': 'admin@sghl.com'}
for p in ['/api/core/reports', '/api/core/users', '/api/core/login-history']:
    try:
        st, _ = get(p, admin_h)
        check(f'GET {p} (admin)', st == 200)
    except Exception as e:
        check(f'GET {p} (admin)', False, str(e))

# Patient login
try:
    _, pat = post('/api/auth/quick-login', {'email': 'patient@sghl.com'})
    check('Patient quick-login', pat.get('success') and pat.get('patient_id'), f"id={pat.get('patient_id')}")
except Exception as e:
    check('Patient quick-login', False, str(e))

# Vite
try:
    req = urllib.request.Request('http://localhost:5173/')
    with urllib.request.urlopen(req, timeout=5) as r:
        html = r.read().decode()
        check('Vite frontend :5173', r.status == 200 and 'SGHL' in html)
except Exception as e:
    warnings.append(f'Vite non accessible sur :5173 — lancez npm run dev ({e})')
    print(f'[WARN] Vite :5173 — {e}')

print('\n=== Résumé ===')
print(f'Erreurs: {len(errors)}')
print(f'Avertissements: {len(warnings)}')
for w in warnings:
    print(f'  ⚠ {w}')
sys.exit(1 if errors else 0)
