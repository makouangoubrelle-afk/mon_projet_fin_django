from datetime import date, timedelta, datetime

from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model

from django.utils import timezone

from admission.models import Patient, Assurance, RendezVous

from clinical.models import Service, Chambre, Lit, BanqueSang, LocalisationPatient, SalleAttente, CasUrgence

from consultation.models import Consultation, Ordonnance

from laboratory.models import Analyse

from billing.models import Facture



User = get_user_model()





class Command(BaseCommand):

    help = 'Initialise SGHL avec services, comptes demo, banque de sang et patients'



    def handle(self, *args, **options):

        self.stdout.write('Initialisation SGHL...')



        services_data = [

            ('CARDIO', 'Cardiologie', 'Bâtiment A', '2', '+242 06 900 001'),

            ('PEDIA', 'Pédiatrie', 'Bâtiment B', '1', '+242 06 900 002'),

            ('URG', 'Urgences', 'Bâtiment A', 'RDC', '+242 06 900 003'),

            ('LABO', 'Laboratoire', 'Bâtiment C', '1', '+242 06 900 004'),

            ('RADIO', 'Radiologie', 'Bâtiment C', '2', '+242 06 900 005'),

        ]

        services = {}

        for code, nom, bat, etage, tel in services_data:

            s, _ = Service.objects.get_or_create(

                code=code,

                defaults={'nom': nom, 'batiment': bat, 'etage': etage, 'telephone': tel},

            )

            services[code] = s



        users_data = [

            ('admin', 'admin123', 'ADMIN', 'admin@sghl.com', 'Admin', 'SGHL', None, '+242 06 900 100'),

            ('secgenerale', 'secgen123', 'SECRETAIRE_GENERALE', 'secgenerale@sghl.com', 'Claire', 'Mukendi', None, '+242 06 900 101'),

            ('medecin', 'medecin123', 'MEDECIN', 'medecin@sghl.com', 'Dr. Jean', 'Kabongo', services['CARDIO'], '+242 06 900 102'),

            ('infirmier', 'infirmier123', 'INFIRMIER', 'infirmier@sghl.com', 'Marie', 'Mputu', services['URG'], '+242 06 900 103'),

            ('secretaire', 'sec123', 'SECRETAIRE', 'secretaire@sghl.com', 'Grace', 'Ilunga', services['CARDIO'], '+242 06 900 104'),

            ('secretaire_pedia', 'secpedia123', 'SECRETAIRE', 'secretaire.pedia@sghl.com', 'Amina', 'Kasongo', services['PEDIA'], '+242 06 900 105'),

            ('reception', 'recep123', 'RECEPTIONNISTE', 'reception@sghl.com', 'Paul', 'Tshibanda', None, '+242 06 900 106'),

            ('patient', 'patient123', 'PATIENT', 'patient@sghl.com', 'Patient', 'Demo', None, '+242 06 900 200'),

        ]

        for username, password, role, email, first, last, service, telephone in users_data:

            user, created = User.objects.get_or_create(username=username, defaults={

                'email': email,

                'first_name': first,

                'last_name': last,

                'role': role,

                'service': service,

                'telephone': telephone,

            })

            if created:

                user.set_password(password)

                user.save()

                self.stdout.write(f'  Compte créé: {email} ({role})')

            else:

                user.email = email

                user.role = role

                user.service = service

                user.telephone = telephone

                user.set_password(password)

                user.save()



        sec = User.objects.get(username='secretaire')
        sec_pedia = User.objects.get(username='secretaire_pedia')

        services['CARDIO'].secretaire = sec

        services['CARDIO'].save()

        services['PEDIA'].secretaire = sec_pedia

        services['PEDIA'].save()

        from users.models import Docteur, Infirmier
        medecin_user = User.objects.get(username='medecin')
        docteur, _ = Docteur.objects.get_or_create(
            email='medecin@sghl.com',
            defaults={
                'nom': 'Kabongo', 'prenom': 'Jean', 'specialite': 'Cardiologie',
                'telephone': medecin_user.telephone, 'user': medecin_user,
                'service': services['CARDIO'], 'est_actif': True,
            },
        )
        docteur.telephone = medecin_user.telephone
        docteur.save(update_fields=['telephone'])
        docteur.services.set([services['CARDIO'].id, services['PEDIA'].id, services['LABO'].id])
        infirmier_user = User.objects.get(username='infirmier')
        inf, _ = Infirmier.objects.get_or_create(
            email='infirmier@sghl.com',
            defaults={
                'nom': 'Mputu', 'prenom': 'Marie', 'telephone': infirmier_user.telephone,
                'user': infirmier_user, 'service': services['URG'], 'est_actif': True, 'en_pause': False,
            },
        )
        inf.telephone = infirmier_user.telephone
        inf.save(update_fields=['telephone'])
        Infirmier.objects.get_or_create(
            email='infirmier2@sghl.com',
            defaults={
                'nom': 'Ngoma', 'prenom': 'Clarisse', 'telephone': '+242 06 900 201',
                'service': services['CARDIO'], 'est_actif': True, 'en_pause': True,
            },
        )

        assurance, _ = Assurance.objects.get_or_create(

            code_assurance='CNSS',

            defaults={'nom': 'CNSS', 'taux_couverture': 80},

        )



        patient_user = User.objects.get(username='patient')

        medecin = User.objects.get(username='medecin')

        patient, _ = Patient.objects.get_or_create(

            sgl_id='SGHL-2026-001',

            defaults={

                'nom': 'Mukendi',

                'prenom': 'Joseph',

                'date_naissance': date(1990, 5, 15),

                'genre': 'M',

                'telephone': '+242 06 812 345',

                'adresse': 'Pointe-Noire, Av. du Commerce 12',

                'groupe_sanguin': 'O+',

                'informations_medicales': (

                    'Allergie : Pénicilline\n'

                    'Antécédents : Hypertension légère\n'

                    'Maladies chroniques : Aucune\n'

                    'Traitement en cours : Amlodipine 5mg/jour'

                ),

                'assurance': assurance,

                'user': patient_user,

            },

        )

        patient.groupe_sanguin = 'O+'

        patient.informations_medicales = patient.informations_medicales or (

            'Allergie : Pénicilline\nAntécédents : Hypertension légère'

        )

        patient.adresse = patient.adresse or 'Kinshasa, Gombe — Av. du Commerce 12'

        if not patient.user_id:

            patient.user = patient_user

        patient.save()
        patient.email = 'patient@sghl.com'
        patient.save(update_fields=['email'])



        patients_extra = [

            ('SGHL-2026-002', 'Kabila', 'Anne', 'F', date(1985, 3, 20), 'A+', 'Bâtiment B', -4.7700, 11.8672),

            ('SGHL-2026-003', 'Lubala', 'Pierre', 'M', date(1978, 11, 8), 'B+', 'Bâtiment C', -4.7684, 11.8656),

        ]

        for sgl_id, nom, prenom, genre, dob, gs, bat, lat, lng in patients_extra:

            p, _ = Patient.objects.get_or_create(

                sgl_id=sgl_id,

                defaults={

                    'nom': nom, 'prenom': prenom, 'genre': genre,

                    'date_naissance': dob, 'telephone': '+242 06 800 000',

                    'adresse': 'Pointe-Noire', 'groupe_sanguin': gs,

                },

            )

            if not LocalisationPatient.objects.filter(patient=p).exists():

                LocalisationPatient.objects.create(

                    patient=p, batiment=bat, etage='1',

                    salle=f'Salle d\'attente — {bat}',

                    latitude=lat, longitude=lng, statut='EN_ATTENTE',

                )



        chambre, _ = Chambre.objects.get_or_create(

            numero='101',

            defaults={

                'type_chambre': 'STANDARD',

                'prix_journalier': 50000,

                'batiment': 'Bâtiment A',

                'etage': '2',

                'service': services['CARDIO'],

            },

        )

        Lit.objects.get_or_create(chambre=chambre, code_lit='A', defaults={'est_occupe': False})

        Lit.objects.get_or_create(chambre=chambre, code_lit='B', defaults={'est_occupe': False})



        chambre2, _ = Chambre.objects.get_or_create(

            numero='201',

            defaults={

                'type_chambre': 'VIP',

                'prix_journalier': 120000,

                'batiment': 'Bâtiment B',

                'etage': '1',

                'service': services['PEDIA'],

            },

        )

        Lit.objects.get_or_create(chambre=chambre2, code_lit='A', defaults={'est_occupe': False})



        if not BanqueSang.objects.exists():

            groupes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

            for i, g in enumerate(groupes):

                for j in range(3):

                    BanqueSang.objects.create(

                        groupe_sanguin=g,

                        numero_poche=f'BS-{g.replace("+","P").replace("-","M")}-{i}{j}',

                        volume_ml=450,

                        date_collecte=date.today() - timedelta(days=10),

                        date_expiration=date.today() + timedelta(days=30 + j * 5),

                        statut='DISPONIBLE',

                    )



        LocalisationPatient.objects.filter(patient=patient).delete()

        LocalisationPatient.objects.create(

            patient=patient,

            service=services['CARDIO'],

            batiment='Bâtiment A',

            etage='2',

            salle='Salle d\'attente — Cardiologie',

            latitude=-4.7692,

            longitude=11.8664,

            statut='EN_ATTENTE',

        )



        if not Consultation.objects.filter(patient=patient).exists():

            Consultation.objects.create(

                patient=patient, medecin=medecin,

                motif_consultation='Contrôle tension artérielle',

                diagnostic='Hypertension légère — surveillance',

                tension_arterielle='14/9', temperature=36.8, poids=78.5, pouls=72,

                notes_medicales='Repos recommandé, rééducation alimentaire',

            )



        if not RendezVous.objects.filter(patient=patient).exists():

            RendezVous.objects.create(

                patient=patient, medecin=medecin, service=services['CARDIO'],

                date_rdv=timezone.now() + timedelta(days=7),

                motif='Suivi cardiologique', statut='CONFIRME',

            )

            RendezVous.objects.create(

                patient=patient, medecin=medecin, service=services['LABO'],

                date_rdv=timezone.now() + timedelta(days=14),

                motif='Bilan sanguin de contrôle', statut='PLANIFIE',

            )

        RendezVous.objects.get_or_create(
            patient=patient, motif='Consultation de contrôle',
            defaults={
                'medecin': medecin, 'service': services['CARDIO'],
                'date_rdv': timezone.now() + timedelta(days=1, hours=2),
                'statut': 'PLANIFIE', 'notes': 'Jeûne 8h avant examen',
            },
        )
        RendezVous.objects.get_or_create(
            patient=patient, motif='Résultats analyses',
            defaults={
                'medecin': medecin, 'service': services['CARDIO'],
                'date_rdv': timezone.now() + timedelta(days=3, hours=4),
                'statut': 'CONFIRME',
            },
        )

        from admission.models import NotePatient
        sec = User.objects.get(username='secretaire')
        if not NotePatient.objects.filter(patient=patient).exists():
            NotePatient.objects.create(
                patient=patient, auteur=sec, medecin=medecin,
                contenu='Patient ponctuel. Préfère les RDV le matin.',
                est_important=False,
            )
            NotePatient.objects.create(
                patient=patient, auteur=sec, medecin=medecin,
                contenu='Allergie pénicilline confirmée — à rappeler au médecin.',
                est_important=True,
            )



        if not Ordonnance.objects.filter(patient=patient).exists():

            Ordonnance.objects.create(

                patient=patient, medecin=medecin,

                medicaments='Amlodipine 5mg — 1 comprimé le matin\nParacétamol 500mg — si douleur',

                instructions='Prendre avec un repas. Ne pas dépasser 3g/jour de paracétamol.',

            )



        if not Analyse.objects.filter(patient_dossier=patient).exists():

            Analyse.objects.create(

                patient=patient_user, patient_dossier=patient,

                examen_nom='Numération formule sanguine',

                statut='VALIDE', resultat='Hémoglobine : 14.2 g/dL — Normale\nLeucocytes : 7200/mm³',

                date_validation=timezone.now(),

            )

            Analyse.objects.create(

                patient=patient_user, patient_dossier=patient,

                examen_nom='Glycémie à jeun',

                statut='VALIDE', resultat='0.92 g/L — Normale',

                date_validation=timezone.now(),

            )



        facture = Facture.objects.filter(patient=patient, statut='EN_ATTENTE').first()
        created = False
        if not facture:
            facture = Facture.objects.create(patient=patient, statut='EN_ATTENTE')
            created = True

        if created or facture.montant_total_brut == 0:

            facture.calculer_facture()

            facture.save()

        from admission.models import ClientPrivilegie
        from billing.models import CompteBanque
        ClientPrivilegie.objects.get_or_create(
            patient=patient,
            defaults={'numero_carte': 'VIP-SGHL-001', 'type_carte': 'VIP', 'taux_reduction': 15, 'est_actif': True},
        )
        CompteBanque.objects.get_or_create(
            numero_compte='00123456789',
            defaults={'nom': 'Compte principal SGHL', 'banque': 'Rawbank', 'solde': 5000000, 'devise': 'CDF'},
        )

        from pharmacy.models import Medicament, PrescriptionPharmacie
        meds_data = [
            ('Paracétamol 500mg', 120, 500),
            ('Amoxicilline 1g', 45, 2500),
            ('Amlodipine 5mg', 80, 1800),
            ('Insuline', 15, 12000),
            ('Sérum physiologique', 200, 800),
        ]
        for nom, qty, prix in meds_data:
            Medicament.objects.get_or_create(nom=nom, defaults={'quantite_en_stock': qty, 'prix_unitaire': prix})

        paracetamol = Medicament.objects.filter(nom__icontains='Paracétamol').first()
        if paracetamol and not PrescriptionPharmacie.objects.filter(patient=patient).exists():
            PrescriptionPharmacie.objects.create(
                patient=patient, medicament=paracetamol, quantite_delivree=2,
            )

        demo_patients = [
            ('U83274', 'alaoui', 'anas', 'M', date(2004, 1, 12), '084238432', 'Célibataire', 'O+'),
            ('U99102', 'AZIZ', 'AZIZI', 'M', date(1980, 6, 5), '081122334', 'Marié(e)', 'A+'),
            ('U77441', 'imane', 'rochdi', 'F', date(1995, 9, 18), '066112233', 'Célibataire', 'B+'),
            ('U66500', 'FATIMA', 'DEMO', 'F', date(1958, 12, 7), '0666666', 'Marié(e)', 'AB+'),
        ]
        for identite, nom, prenom, genre, dob, tel, situation, gs in demo_patients:
            p, created = Patient.objects.get_or_create(
                numero_identite=identite,
                defaults={
                    'sgl_id': f'SGHL-DEMO-{identite}',
                    'nom': nom, 'prenom': prenom, 'genre': genre,
                    'date_naissance': dob, 'telephone': tel,
                    'adresse': 'Pointe-Noire', 'situation_familiale': situation,
                    'groupe_sanguin': gs, 'profession': 'PROFESSEUR' if nom == 'FATIMA' else None,
                    'poids_kg': 65 if nom == 'FATIMA' else None,
                    'taille_m': 1.57 if nom == 'FATIMA' else None,
                    'nombre_enfants': 3 if nom == 'FATIMA' else 0,
                    'assurance': assurance,
                },
            )
            if not SalleAttente.objects.filter(patient=p, statut='EN_ATTENTE').exists():
                SalleAttente.objects.create(patient=p, motif='Consultation générale', priorite='NORMAL')
            if nom == 'FATIMA':
                CasUrgence.objects.get_or_create(
                    patient=p, diagnostic='HBP',
                    defaults={'situation': 'IMPORTANT', 'examen_radiologique': 'ECHOGRAPHIE RÉNO-VÉSICO-PELVIENNE'},
                )
            elif nom == 'alaoui':
                CasUrgence.objects.get_or_create(
                    patient=p, diagnostic='Infection urinaire',
                    defaults={'situation': 'NORMAL'},
                )

        portal_accounts = [
            ('alaoui.anas@patient.sghl.com', 'U83274'),
            ('fatima.demo@patient.sghl.com', 'U66500'),
            ('imane.rochdi@patient.sghl.com', 'U77441'),
            ('aziz.azizi@patient.sghl.com', 'U99102'),
        ]
        for email, identite in portal_accounts:
            p = Patient.objects.filter(numero_identite=identite).first()
            if not p:
                continue
            username = email.split('@')[0].replace('.', '_')
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': p.prenom,
                    'last_name': p.nom,
                    'role': 'PATIENT',
                },
            )
            user.role = 'PATIENT'
            if not user.has_usable_password():
                user.set_password('patient123')
            user.save()
            p.email = email
            p.user = user
            p.save(update_fields=['email', 'user'])

        demo_dossiers = [
            ('U83274', 'Amoxicilline 1g — 1 cp matin et soir\nParacétamol 500mg — si douleur'),
            ('U66500', 'Tamsulosine 0,4mg — 1 gélule le soir\nParacétamol 500mg — si douleur'),
            ('U77441', 'Vitamine D — 1 ampoule par semaine'),
            ('U99102', 'Ibuprofène 400mg — 3 fois par jour après repas'),
        ]
        for identite, meds in demo_dossiers:
            p = Patient.objects.filter(numero_identite=identite).first()
            if not p:
                continue
            Ordonnance.objects.get_or_create(
                patient=p,
                medicaments=meds,
                defaults={
                    'medecin': medecin,
                    'instructions': 'Suivre le traitement prescrit par le médecin.',
                },
            )
            if not Analyse.objects.filter(patient_dossier=p).exists():
                u = p.user or patient_user
                Analyse.objects.create(
                    patient=u,
                    patient_dossier=p,
                    examen_nom='Bilan sanguin',
                    statut='VALIDE',
                    resultat='Numération et ionogramme — résultats dans les normes.',
                    date_validation=timezone.now(),
                )

        self.stdout.write(self.style.SUCCESS('SGHL initialisé avec succès !'))

        self.stdout.write('Comptes: admin/admin123, medecin/medecin123, infirmier/infirmier123, secretaire/sec123, patient/patient123')
        self.stdout.write('Portail patients (OTP email): patient@sghl.com, alaoui.anas@patient.sghl.com, fatima.demo@patient.sghl.com, imane.rochdi@patient.sghl.com')

